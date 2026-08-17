use crate::course::{Course, Position};
use crate::simulation::SimulationResult;

const PROGRESS_REWARD_PER_CELL: f64 = 15.0;
const UNIQUE_CELL_REWARD: f64 = 10.0;
const SUCCESSFUL_MOVE_REWARD: f64 = 0.02;
const COLLISION_PENALTY: f64 = 0.25;

const GOAL_REWARD: f64 = 10_000.0;
const SOLUTION_STEP_PENALTY: f64 = 0.5;

pub fn calculate(
    result: &SimulationResult,
    course: &Course,
) -> f64 {
    let distances_to_goal =
        shortest_distances_to_goal(course);

    let start_distance =
        distances_to_goal[course.start.y * course.width + course.start.x]
            .expect("Course start must be reachable from goal");

    let closest_distance = result
        .path
        .iter()
        .filter_map(|position| {
            distances_to_goal[
                position.y * course.width + position.x
            ]
        })
        .min()
        .unwrap_or(start_distance);

    let progress =
        start_distance.saturating_sub(closest_distance);

    let unique_cells =
        count_unique_cells(&result.path, course);

    let successful_moves =
        result.path.len().saturating_sub(1);

    let mut fitness = 0.0;

    fitness +=
        progress as f64
            * PROGRESS_REWARD_PER_CELL;

    fitness +=
        unique_cells as f64
            * UNIQUE_CELL_REWARD;

    fitness +=
        successful_moves as f64
            * SUCCESSFUL_MOVE_REWARD;

    fitness -=
        result.collisions as f64
            * COLLISION_PENALTY;

    if result.reached_goal {
        fitness += GOAL_REWARD;

        fitness -=
            result.steps as f64
                * SOLUTION_STEP_PENALTY;
    }

    fitness
}

fn count_unique_cells(
    path: &[Position],
    course: &Course,
) -> usize {
    let mut visited =
        vec![false; course.width * course.height];

    let mut unique_count = 0;

    for position in path {
        let index =
            position.y * course.width + position.x;

        if !visited[index] {
            visited[index] = true;
            unique_count += 1;
        }
    }

    unique_count
}

fn shortest_distances_to_goal(
    course: &Course,
) -> Vec<Option<usize>> {
    use std::collections::VecDeque;

    let mut distances =
        vec![None; course.width * course.height];

    let mut queue = VecDeque::new();

    let goal_index =
        course.goal.y * course.width + course.goal.x;

    distances[goal_index] = Some(0);
    queue.push_back(course.goal);

    while let Some(current) = queue.pop_front() {
        let current_index =
            current.y * course.width + current.x;

        let current_distance =
            distances[current_index]
                .expect("Queued position must have a distance");

        let neighbors = [
            current
                .x
                .checked_sub(1)
                .map(|x| Position {
                    x,
                    y: current.y,
                }),

            (current.x + 1 < course.width)
                .then_some(Position {
                    x: current.x + 1,
                    y: current.y,
                }),

            current
                .y
                .checked_sub(1)
                .map(|y| Position {
                    x: current.x,
                    y,
                }),

            (current.y + 1 < course.height)
                .then_some(Position {
                    x: current.x,
                    y: current.y + 1,
                }),
        ];

        for neighbor in neighbors.into_iter().flatten() {
            if !course.is_walkable(neighbor) {
                continue;
            }

            let neighbor_index =
                neighbor.y * course.width + neighbor.x;

            if distances[neighbor_index].is_some() {
                continue;
            }

            distances[neighbor_index] =
                Some(current_distance + 1);

            queue.push_back(neighbor);
        }
    }

    distances
}