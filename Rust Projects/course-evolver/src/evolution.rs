use crate::course::Course;
use crate::job::Job;
use crate::policy::RandomPolicy;

pub struct Evolution {
    population: Vec<RandomPolicy>,
    next_job_id: u64,
    max_steps: usize,
}

impl Evolution {
    pub fn new(
        population_size: usize,
        max_steps: usize,
    ) -> Self {
        let mut population = Vec::with_capacity(population_size);

        for _ in 0..population_size {
            population.push(RandomPolicy::new());
        }

        Self {
            population,
            next_job_id: 0,
            max_steps,
        }
    }

    pub fn create_jobs(&mut self) -> Vec<Job> {
        let mut jobs = Vec::with_capacity(self.population.len());

        for policy in &self.population {
            let course = Course::random(50, 50);

            let job = Job::new(
                self.next_job_id,
                course,
                Box::new(policy.clone()),
                self.max_steps,
            );

            self.next_job_id += 1;

            jobs.push(job);
        }

        jobs
    }
}