# Concurrent Go Webcam

Small Go experiment for learning real-time video capture, rendering, and concurrency.

## Features

* Webcam capture via `gocam` (Windows Media Foundation)
* Rendering with Ebiten
* Concurrent frame capture and FPS calculation using goroutines/channels
* Mutex-protected shared rendering state

## Run

```bash
go run .
```

## Requirements

* Windows
* Go with CGO enabled
* Webcam
