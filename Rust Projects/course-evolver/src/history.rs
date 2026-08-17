use crate::job::JobResult;

pub struct GenerationRecord {
    pub generation: usize,
    pub results: Vec<JobResult>,
}

impl GenerationRecord {
    pub fn new(
        generation: usize,
        results: Vec<JobResult>,
    ) -> Self {
        Self {
            generation,
            results,
        }
    }
}