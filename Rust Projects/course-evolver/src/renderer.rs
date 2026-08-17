use macroquad::prelude::*;

use crate::app::App;
use crate::course::{Cell, Position};
use crate::history::GenerationRecord;
use crate::job::JobResult;

const CELL_SIZE: f32 = 12.0;

pub fn render(
    app: &App,
    history: &[GenerationRecord],
) {
    clear_background(WHITE);

    let Some(generation_index) =
        app.selected_generation
    else {
        draw_text(
            "Waiting for generation results...",
            30.0,
            50.0,
            28.0,
            BLACK,
        );

        return;
    };

    let generation =
        &history[generation_index];

    let Some(result_index) =
        app.selected_result
    else {
        return;
    };

    let result =
        &generation.results[result_index];

    draw_course(result);
    draw_path(app, result);

    draw_information(
        app,
        history,
        generation_index,
        generation,
        result,
        result_index,
    );
}

fn draw_course(result: &JobResult) {
    let course = &result.course;

    for y in 0..course.height {
        for x in 0..course.width {
            let position = Position { x, y };

            let color =
                if position == course.start {
                    GREEN
                } else if position == course.goal {
                    RED
                } else {
                    match course.cell(position) {
                        Cell::Open => LIGHTGRAY,
                        Cell::Obstacle => DARKGRAY,
                    }
                };

            draw_rectangle(
                x as f32 * CELL_SIZE,
                y as f32 * CELL_SIZE,
                CELL_SIZE - 1.0,
                CELL_SIZE - 1.0,
                color,
            );
        }
    }
}

fn draw_path(
    app: &App,
    result: &JobResult,
) {
    let path = &result.simulation.path;

    if path.is_empty() {
        return;
    }

    let playback_index =
        app.playback_index.min(path.len() - 1);

    let visible_path =
        &path[..=playback_index];

    for window in visible_path.windows(2) {
        let first = window[0];
        let second = window[1];

        let x1 =
            first.x as f32 * CELL_SIZE
                + CELL_SIZE / 2.0;

        let y1 =
            first.y as f32 * CELL_SIZE
                + CELL_SIZE / 2.0;

        let x2 =
            second.x as f32 * CELL_SIZE
                + CELL_SIZE / 2.0;

        let y2 =
            second.y as f32 * CELL_SIZE
                + CELL_SIZE / 2.0;

        draw_line(
            x1,
            y1,
            x2,
            y2,
            2.0,
            BLUE,
        );
    }

    let current =
        path[playback_index];

    let agent_x =
        current.x as f32 * CELL_SIZE
            + CELL_SIZE / 2.0;

    let agent_y =
        current.y as f32 * CELL_SIZE
            + CELL_SIZE / 2.0;

    draw_circle(
        agent_x,
        agent_y,
        CELL_SIZE * 0.35,
        BLUE,
    );
}

fn draw_information(
    app: &App,
    history: &[GenerationRecord],
    generation_index: usize,
    generation: &GenerationRecord,
    result: &JobResult,
    result_index: usize,
) {
    let panel_x =
        result.course.width as f32
            * CELL_SIZE
            + 20.0;

    draw_text(
        "Course Evolver",
        panel_x,
        40.0,
        28.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Generation: {} / {}",
            generation_index + 1,
            history.len()
        ),
        panel_x,
        80.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Generation ID: {}",
            generation.generation
        ),
        panel_x,
        110.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Individual: {}",
            result.individual_id
        ),
        panel_x,
        140.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Result: {} / {}",
            result_index + 1,
            generation.results.len()
        ),
        panel_x,
        170.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!("Job: {}", result.job_id),
        panel_x,
        200.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Fitness: {:.2}",
            result.fitness
        ),
        panel_x,
        230.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Steps: {}",
            result.simulation.steps
        ),
        panel_x,
        260.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Collisions: {}",
            result.simulation.collisions
        ),
        panel_x,
        290.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Reached goal: {}",
            result.simulation.reached_goal
        ),
        panel_x,
        320.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Playback: {}",
            app.playback_index
        ),
        panel_x,
        370.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Speed: {:.0} steps/sec",
            app.playback_speed
        ),
        panel_x,
        400.0,
        22.0,
        BLACK,
    );

    let playback_status =
        if app.playing {
            "Playing"
        } else {
            "Paused"
        };

    draw_text(
        playback_status,
        panel_x,
        430.0,
        22.0,
        BLACK,
    );

    draw_text(
        "PageUp/PageDown: generation",
        panel_x,
        480.0,
        18.0,
        BLACK,
    );

    draw_text(
        "Left/Right: individual",
        panel_x,
        505.0,
        18.0,
        BLACK,
    );

    draw_text(
        "B: best individual",
        panel_x,
        530.0,
        18.0,
        BLACK,
    );

    draw_text(
        "Space: play/pause",
        panel_x,
        555.0,
        18.0,
        BLACK,
    );

    draw_text(
        "R: restart",
        panel_x,
        580.0,
        18.0,
        BLACK,
    );

    draw_text(
        "Up/Down: speed",
        panel_x,
        605.0,
        18.0,
        BLACK,
    );
}