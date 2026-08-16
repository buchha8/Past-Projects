use crate::course::Course;
use crate::simulation::SimulationResult;

pub fn calculate(result: &SimulationResult, course: &Course) -> f64 {
    let distance_to_goal = manhattan_distance(result.final_position, course.goal);

    let mut fitness = 0.0;

    // Getting closer to the goal is better.
    fitness += 1_000.0 / (1.0 + distance_to_goal as f64);

    // Successful movement is better than repeatedly colliding.
    fitness -= result.collisions as f64 * 0.5;

    // Shorter solutions are preferable once the goal is reached.
    if result.reached_goal {
        fitness += 10_000.0;
        fitness -= result.steps as f64;
    }

    fitness
}

fn manhattan_distance(a: crate::course::Position, b: crate::course::Position) -> usize {
    a.x.abs_diff(b.x) + a.y.abs_diff(b.y)
}