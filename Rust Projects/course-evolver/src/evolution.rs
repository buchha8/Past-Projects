use std::sync::Arc;

use rand::Rng;

use crate::course::Course;
use crate::job::{Job, JobResult};
use crate::policy::{Genome, RecurrentPolicy};

const ELITE_COUNT: usize = 2;
const MUTATION_RATE: f64 = 0.10;
const MUTATION_AMOUNT: f32 = 0.25;
const MIN_WEIGHT: f32 = -3.0;
const MAX_WEIGHT: f32 = 3.0;

#[derive(Clone, Debug)]
pub struct Individual {
    pub id: u64,
    pub genome: Genome,
}

pub struct Evolution {
    population: Vec<Individual>,
    generation: usize,
    next_individual_id: u64,
    next_job_id: u64,
    max_steps: usize,
}

impl Evolution {
    pub fn new(
        population_size: usize,
        max_steps: usize,
    ) -> Self {
        let mut next_individual_id = 0;

        let population = (0..population_size)
            .map(|_| {
                let individual = Individual {
                    id: next_individual_id,
                    genome: Genome::random(),
                };

                next_individual_id += 1;

                individual
            })
            .collect();

        Self {
            population,
            generation: 0,
            next_individual_id,
            next_job_id: 0,
            max_steps,
        }
    }

    pub fn create_jobs(&mut self) -> Vec<Job> {
        let course = Arc::new(Course::random(50, 50));

        let mut jobs =
            Vec::with_capacity(self.population.len());

        for individual in &self.population {
            let policy =
                RecurrentPolicy::new(individual.genome.clone());

            let job = Job::new(
                self.next_job_id,
                self.generation,
                individual.id,
                Arc::clone(&course),
                Box::new(policy),
                self.max_steps,
            );

            self.next_job_id += 1;

            jobs.push(job);
        }

        jobs
    }

    pub fn advance_generation(
        &mut self,
        results: &[JobResult],
    ) {
        assert_eq!(
            results.len(),
            self.population.len(),
            "Every individual must have exactly one result"
        );

        let mut ranked_results: Vec<&JobResult> =
            results.iter().collect();

        ranked_results.sort_by(|a, b| {
            b.fitness.total_cmp(&a.fitness)
        });

        let ranked_population: Vec<Individual> =
            ranked_results
                .iter()
                .map(|result| {
                    self.population
                        .iter()
                        .find(|individual| {
                            individual.id
                                == result.individual_id
                        })
                        .expect(
                            "Job result references unknown individual",
                        )
                        .clone()
                })
                .collect();

        let population_size = self.population.len();

        let elite_count =
            ELITE_COUNT.min(population_size);

        let parent_pool_size =
            (population_size / 2).max(1);

        let mut next_population =
            Vec::with_capacity(population_size);

        for elite in ranked_population
            .iter()
            .take(elite_count)
        {
            next_population.push(elite.clone());
        }

        let mut rng = rand::rng();

        while next_population.len() < population_size {
            let parent_a =
                &ranked_population[
                    rng.random_range(0..parent_pool_size)
                ];

            let parent_b =
                &ranked_population[
                    rng.random_range(0..parent_pool_size)
                ];

            let mut child_genome = crossover(
                &parent_a.genome,
                &parent_b.genome,
                &mut rng,
            );

            mutate(
                &mut child_genome,
                &mut rng,
            );

            let child = Individual {
                id: self.next_individual_id,
                genome: child_genome,
            };

            self.next_individual_id += 1;

            next_population.push(child);
        }

        self.population = next_population;
        self.generation += 1;
    }

    pub fn generation(&self) -> usize {
        self.generation
    }
}

fn crossover(
    parent_a: &Genome,
    parent_b: &Genome,
    rng: &mut impl Rng,
) -> Genome {
    Genome {
        input_hidden_weights:
            std::array::from_fn(|index| {
                choose_parent_weight(
                    parent_a.input_hidden_weights[index],
                    parent_b.input_hidden_weights[index],
                    rng,
                )
            }),

        hidden_hidden_weights:
            std::array::from_fn(|index| {
                choose_parent_weight(
                    parent_a.hidden_hidden_weights[index],
                    parent_b.hidden_hidden_weights[index],
                    rng,
                )
            }),

        hidden_biases:
            std::array::from_fn(|index| {
                choose_parent_weight(
                    parent_a.hidden_biases[index],
                    parent_b.hidden_biases[index],
                    rng,
                )
            }),

        hidden_action_weights:
            std::array::from_fn(|index| {
                choose_parent_weight(
                    parent_a.hidden_action_weights[index],
                    parent_b.hidden_action_weights[index],
                    rng,
                )
            }),

        action_biases:
            std::array::from_fn(|index| {
                choose_parent_weight(
                    parent_a.action_biases[index],
                    parent_b.action_biases[index],
                    rng,
                )
            }),
    }
}

fn choose_parent_weight(
    parent_a: f32,
    parent_b: f32,
    rng: &mut impl Rng,
) -> f32 {
    if rng.random_bool(0.5) {
        parent_a
    } else {
        parent_b
    }
}

fn mutate(
    genome: &mut Genome,
    rng: &mut impl Rng,
) {
    for weight in genome
        .input_hidden_weights
        .iter_mut()
        .chain(genome.hidden_hidden_weights.iter_mut())
        .chain(genome.hidden_biases.iter_mut())
        .chain(genome.hidden_action_weights.iter_mut())
        .chain(genome.action_biases.iter_mut())
    {
        if rng.random_bool(MUTATION_RATE) {
            *weight += rng.random_range(
                -MUTATION_AMOUNT..=MUTATION_AMOUNT,
            );

            *weight =
                weight.clamp(MIN_WEIGHT, MAX_WEIGHT);
        }
    }
}