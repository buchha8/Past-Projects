use crate::course::{Course, Position};
use crate::policy::{observe, Action, Policy};

pub struct Agent {
    pub position: Position,
    pub path: Vec<Position>,
    pub collisions: usize,
}

impl Agent {
    pub fn new(start: Position) -> Self {
        Self {
            position: start,
            path: vec![start],
            collisions: 0,
        }
    }
}

pub struct Simulation<P: Policy> {
    pub course: Course,
    pub policy: P,
    pub agent: Agent,
    pub steps: usize,
    pub max_steps: usize,
    pub finished: bool,
    pub reached_goal: bool,
}

impl<P: Policy> Simulation<P> {
    pub fn new(course: Course, policy: P, max_steps: usize) -> Self {
        let start = course.start;

        Self {
            course,
            policy,
            agent: Agent::new(start),
            steps: 0,
            max_steps,
            finished: false,
            reached_goal: false,
        }
    }

    pub fn step(&mut self) {
        if self.finished {
            return;
        }

        if self.agent.position == self.course.goal {
            self.finished = true;
            self.reached_goal = true;
            return;
        }

        if self.steps >= self.max_steps {
            self.finished = true;
            return;
        }

        let observation = observe(&self.course, self.agent.position);
        let action = self.policy.choose_action(&observation);

        let target = match action {
            Action::Up => Position {
                x: self.agent.position.x,
                y: self.agent.position.y.saturating_sub(1),
            },
            Action::Down => Position {
                x: self.agent.position.x,
                y: self.agent.position.y + 1,
            },
            Action::Left => Position {
                x: self.agent.position.x.saturating_sub(1),
                y: self.agent.position.y,
            },
            Action::Right => Position {
                x: self.agent.position.x + 1,
                y: self.agent.position.y,
            },
        };

        if self.course.is_walkable(target) {
            self.agent.position = target;
            self.agent.path.push(target);
        } else {
            self.agent.collisions += 1;
        }

        self.steps += 1;

        if self.agent.position == self.course.goal {
            self.finished = true;
            self.reached_goal = true;
        } else if self.steps >= self.max_steps {
            self.finished = true;
        }
    }

    pub fn run_to_completion(&mut self) {
        while !self.finished {
            self.step();
        }
    }

    pub fn result(&self) -> SimulationResult {
        SimulationResult {
            reached_goal: self.reached_goal,
            steps: self.steps,
            collisions: self.agent.collisions,
            final_position: self.agent.position,
            path: self.agent.path.clone(),
        }
    }
}

pub struct SimulationResult {
    pub reached_goal: bool,
    pub steps: usize,
    pub collisions: usize,
    pub final_position: Position,
    pub path: Vec<Position>,
}