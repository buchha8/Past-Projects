package main

import (
	"context"
	"fmt"
	"image"
	"image/color"
	"log"
	"sync"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/text"
	"github.com/svanichkin/gocam"
	"golang.org/x/image/font/basicfont"
)

type WebcamApp struct {
	imageMu sync.RWMutex
	img     *ebiten.Image

	fpsMu sync.RWMutex
	fps   float64
}

func (app *WebcamApp) Update() error {
	return nil
}

func (app *WebcamApp) Draw(screen *ebiten.Image) {
	app.imageMu.RLock()
	if app.img != nil {
		screen.DrawImage(app.img, nil)
	}
	app.imageMu.RUnlock()

	app.fpsMu.RLock()
	fps := app.fps
	app.fpsMu.RUnlock()

	text.Draw(
		screen,
		fmt.Sprintf("FPS: %.2f", fps),
		basicfont.Face7x13,
		10,
		20,
		color.RGBA{
			R: 255,
			G: 0,
			B: 0,
			A: 255,
		},
	)
}

func (app *WebcamApp) Layout(outW, outH int) (int, int) {
	app.imageMu.RLock()
	defer app.imageMu.RUnlock()

	if app.img == nil {
		return 352, 288
	}

	return app.img.Bounds().Dx(), app.img.Bounds().Dy()
}

func (app *WebcamApp) SetImage(img *ebiten.Image) {
	app.imageMu.Lock()
	defer app.imageMu.Unlock()

	app.img = img
}

func (app *WebcamApp) SetFPS(fps float64) {
	app.fpsMu.Lock()
	defer app.fpsMu.Unlock()

	app.fps = fps
}

func clamp(v float64) uint8 {
	if v < 0 {
		return 0
	}
	if v > 255 {
		return 255
	}
	return uint8(v)
}

func ycbcrToRGBA(frame gocam.Frame) *image.RGBA {
	img := image.NewRGBA(
		image.Rect(0, 0, frame.Width, frame.Height),
	)

	for y := 0; y < frame.Height; y++ {
		for x := 0; x < frame.Width; x++ {
			i := (y*frame.Width + x) * 3

			if i+2 >= len(frame.Data) {
				continue
			}

			Y := float64(frame.Data[i])
			Cb := float64(frame.Data[i+1]) - 128
			Cr := float64(frame.Data[i+2]) - 128

			r := Y + 1.402*Cr
			g := Y - 0.344136*Cb - 0.714136*Cr
			b := Y + 1.772*Cb

			img.SetRGBA(
				x,
				y,
				color.RGBA{
					R: clamp(r),
					G: clamp(g),
					B: clamp(b),
					A: 255,
				},
			)
		}
	}

	return img
}

func cameraWorker(
	ctx context.Context,
	app *WebcamApp,
	frameCounter chan<- struct{},
) {
	frames, err := gocam.StartStream(ctx)
	if err != nil {
		log.Fatal(err)
	}

	for frame := range frames {
		rgba := ycbcrToRGBA(frame)

		app.SetImage(
			ebiten.NewImageFromImage(rgba),
		)

		// Notify FPS counter without blocking camera capture.
		select {
		case frameCounter <- struct{}{}:
		default:
		}
	}
}

func fpsWorker(
	ctx context.Context,
	app *WebcamApp,
	frameCounter <-chan struct{},
) {
	const windowSize = 30

	timestamps := make([]time.Time, 0, windowSize)

	for {
		select {
		case <-ctx.Done():
			return

		case <-frameCounter:
			now := time.Now()

			timestamps = append(timestamps, now)

			// Keep only the most recent N frame timestamps.
			if len(timestamps) > windowSize {
				timestamps = timestamps[1:]
			}

			// Need at least two timestamps to measure an interval.
			if len(timestamps) >= 2 {
				elapsed := timestamps[len(timestamps)-1].
					Sub(timestamps[0]).
					Seconds()

				fps := float64(len(timestamps)-1) / elapsed

				app.SetFPS(fps)
			}
		}
	}
}

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	app := &WebcamApp{}

	frameCounter := make(chan struct{}, 100)

	go cameraWorker(ctx, app, frameCounter)
	go fpsWorker(ctx, app, frameCounter)

	ebiten.SetWindowSize(704, 576)
	ebiten.SetWindowTitle("Concurrent Go Webcam")

	if err := ebiten.RunGame(app); err != nil {
		log.Fatal(err)
	}
}
