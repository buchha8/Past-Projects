mod app;
mod controller;
mod course;
mod evolution;
mod fitness;
mod job;
mod policy;
mod renderer;
mod scheduler;
mod simulation;

use app::App;
use controller::RunController;
use macroquad::prelude::next_frame;

const WORKER_COUNT: usize = 4;
const POPULATION_SIZE: usize = 12;
const MAX_STEPS: usize = 5_000;

#[macroquad::main("Course Evolver")]
async fn main() {
    let mut controller = RunController::new(
        WORKER_COUNT,
        POPULATION_SIZE,
        MAX_STEPS,
    );

    let mut app = App::new();

    loop {
        controller.update();
        app.update();

        renderer::render(&app.simulation);

        next_frame().await;
    }
}