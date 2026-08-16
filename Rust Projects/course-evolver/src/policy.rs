use rand::Rng;
use rand::SeedableRng;

use crate::course::{Course, Position};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action {
    Up,
    Down,
    Left,
    Right,
}

#[derive(Clone, Copy, Debug)]
pub struct Observation {
    pub position: Position,
    pub up_blocked: bool,
    pub down_blocked: bool,
    pub left_blocked: bool,
    pub right_blocked: bool,
    pub goal_direction_x: i8,
    pub goal_direction_y: i8,
}

pub trait Policy: Send {
    fn choose_action(&mut self, observation: &Observation) -> Action;
}

impl<P: Policy + ?Sized> Policy for Box<P> {
    fn choose_action(&mut self, observation: &Observation) -> Action {
        (**self).choose_action(observation)
    }
}

#[derive(Clone)]
pub struct RandomPolicy {
    rng: rand::rngs::StdRng,
}

impl RandomPolicy {
    pub fn new() -> Self {
        Self {
            rng: rand::rngs::StdRng::from_os_rng(),
        }
    }
}

impl Policy for RandomPolicy {
    fn choose_action(&mut self, _observation: &Observation) -> Action {
        match self.rng.random_range(0..4) {
            0 => Action::Up,
            1 => Action::Down,
            2 => Action::Left,
            _ => Action::Right,
        }
    }
}

pub fn observe(course: &Course, position: Position) -> Observation {
    let up = Position {
        x: position.x,
        y: position.y.saturating_sub(1),
    };

    let down = Position {
        x: position.x,
        y: position.y + 1,
    };

    let left = Position {
        x: position.x.saturating_sub(1),
        y: position.y,
    };

    let right = Position {
        x: position.x + 1,
        y: position.y,
    };

    Observation {
        position,
        up_blocked: !course.is_walkable(up),
        down_blocked: !course.is_walkable(down),
        left_blocked: !course.is_walkable(left),
        right_blocked: !course.is_walkable(right),
        goal_direction_x: (course.goal.x as i32 - position.x as i32).signum() as i8,
        goal_direction_y: (course.goal.y as i32 - position.y as i32).signum() as i8,
    }
}