use crate::course::Course;
use crate::fitness;
use crate::policy::Policy;
use crate::simulation::{Simulation, SimulationResult};

pub struct Job {
    pub id: u64,
    pub course: Course,
    pub policy: Box<dyn Policy>,
    pub max_steps: usize,
}

pub struct JobResult {
    pub job_id: u64,
    pub simulation: SimulationResult,
    pub fitness: f64,
}

impl Job {
    pub fn new(
        id: u64,
        course: Course,
        policy: Box<dyn Policy>,
        max_steps: usize,
    ) -> Self {
        Self {
            id,
            course,
            policy,
            max_steps,
        }
    }

    pub fn execute(self) -> JobResult {
        let job_id = self.id;

        let mut simulation =
            Simulation::new(self.course, self.policy, self.max_steps);

        simulation.run_to_completion();

        let simulation_result = simulation.result();

        let fitness =
            fitness::calculate(&simulation_result, &simulation.course);

        JobResult {
            job_id,
            simulation: simulation_result,
            fitness,
        }
    }
}