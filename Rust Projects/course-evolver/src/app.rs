use crate::course::Course;
use crate::policy::RandomPolicy;
use crate::simulation::Simulation;

pub const COURSE_SIZE: usize = 50;
pub const MAX_STEPS: usize = 5_000;

pub struct App {
    pub simulation: Simulation<RandomPolicy>,
}

impl App {
    pub fn new() -> Self {
        let course = Course::random(COURSE_SIZE, COURSE_SIZE);
        let policy = RandomPolicy::new();

        let simulation = Simulation::new(course, policy, MAX_STEPS);

        Self { simulation }
    }

    pub fn update(&mut self) {
        if !self.simulation.finished {
            self.simulation.step();
        }
    }
}