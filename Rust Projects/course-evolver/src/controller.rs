use std::collections::VecDeque;

use crate::evolution::Evolution;
use crate::job::Job;
use crate::scheduler::Scheduler;

pub struct RunController {
    scheduler: Scheduler,
    evolution: Evolution,

    pending_jobs: VecDeque<Job>,

    expected_jobs: usize,
    completed_jobs: usize,
    generation_complete: bool,
}

impl RunController {
    pub fn new(
        worker_count: usize,
        population_size: usize,
        max_steps: usize,
    ) -> Self {
        let mut controller = Self {
            scheduler: Scheduler::new(worker_count),
            evolution: Evolution::new(
                population_size,
                max_steps,
            ),

            pending_jobs: VecDeque::new(),

            expected_jobs: 0,
            completed_jobs: 0,
            generation_complete: false,
        };

        controller.queue_generation();

        controller
    }

    pub fn update(&mut self) {
        self.submit_pending_jobs();
        self.collect_results();
    }

    fn queue_generation(&mut self) {
        let jobs = self.evolution.create_jobs();

        self.expected_jobs = jobs.len();
        self.completed_jobs = 0;
        self.generation_complete = false;

        self.pending_jobs.extend(jobs);
    }

    fn submit_pending_jobs(&mut self) {
        while let Some(job) = self.pending_jobs.pop_front() {
            match self.scheduler.submit(job) {
                Ok(()) => {}

                Err(job) => {
                    self.pending_jobs.push_front(job);
                    break;
                }
            }
        }
    }

    fn collect_results(&mut self) {
        while let Some(result) = self.scheduler.try_receive() {
            println!(
                "Job {} completed: fitness = {:.2}",
                result.job_id,
                result.fitness
            );

            self.completed_jobs += 1;

            if self.completed_jobs == self.expected_jobs {
                self.generation_complete = true;

                println!("Generation completed.");
            }
        }
    }
}