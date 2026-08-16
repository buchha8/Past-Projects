use macroquad::prelude::*;

use crate::course::Cell;
use crate::policy::Policy;
use crate::simulation::Simulation;

const CELL_SIZE: f32 = 12.0;

pub fn render<P: Policy>(simulation: &Simulation<P>) {
    clear_background(WHITE);

    draw_course(simulation);
    draw_information(simulation);
}

fn draw_course<P: Policy>(simulation: &Simulation<P>) {
    for y in 0..simulation.course.height {
        for x in 0..simulation.course.width {
            let position = crate::course::Position { x, y };

            let color = if position == simulation.course.start {
                GREEN
            } else if position == simulation.course.goal {
                RED
            } else {
                match simulation.course.cell(position) {
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

    for window in simulation.agent.path.windows(2) {
        let first = window[0];
        let second = window[1];

        let x1 = first.x as f32 * CELL_SIZE + CELL_SIZE / 2.0;
        let y1 = first.y as f32 * CELL_SIZE + CELL_SIZE / 2.0;
        let x2 = second.x as f32 * CELL_SIZE + CELL_SIZE / 2.0;
        let y2 = second.y as f32 * CELL_SIZE + CELL_SIZE / 2.0;

        draw_line(x1, y1, x2, y2, 2.0, BLUE);
    }

    let agent_x =
        simulation.agent.position.x as f32 * CELL_SIZE + CELL_SIZE / 2.0;
    let agent_y =
        simulation.agent.position.y as f32 * CELL_SIZE + CELL_SIZE / 2.0;

    draw_circle(agent_x, agent_y, CELL_SIZE * 0.35, BLUE);
}

fn draw_information<P: Policy>(simulation: &Simulation<P>) {
    let panel_x = simulation.course.width as f32 * CELL_SIZE + 20.0;

    draw_text("Course Evolver", panel_x, 40.0, 28.0, BLACK);

    draw_text(
        &format!("Step: {}", simulation.steps),
        panel_x,
        80.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!("Collisions: {}", simulation.agent.collisions),
        panel_x,
        110.0,
        22.0,
        BLACK,
    );

    draw_text(
        &format!(
            "Position: ({}, {})",
            simulation.agent.position.x,
            simulation.agent.position.y
        ),
        panel_x,
        140.0,
        22.0,
        BLACK,
    );

    if simulation.finished {
        let status = if simulation.reached_goal {
            "GOAL REACHED"
        } else {
            "SIMULATION FINISHED"
        };

        draw_text(status, panel_x, 190.0, 24.0, BLACK);
    } else {
        draw_text("Running...", panel_x, 190.0, 24.0, BLACK);
    }
}