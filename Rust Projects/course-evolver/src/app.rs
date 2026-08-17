use macroquad::prelude::{
    get_frame_time,
    is_key_pressed,
    KeyCode,
};

use crate::history::GenerationRecord;
use crate::job::JobResult;

pub struct App {
    pub selected_generation: Option<usize>,
    pub selected_result: Option<usize>,

    pub playback_index: usize,
    pub playing: bool,
    pub playback_speed: f32,

    playback_accumulator: f32,
}

impl App {
    pub fn new() -> Self {
        Self {
            selected_generation: None,
            selected_result: None,

            playback_index: 0,
            playing: true,
            playback_speed: 30.0,

            playback_accumulator: 0.0,
        }
    }

    pub fn update(
        &mut self,
        history: &[GenerationRecord],
    ) {
        if history.is_empty() {
            self.selected_generation = None;
            self.selected_result = None;
            return;
        }

        if self.selected_generation.is_none() {
            self.selected_generation = Some(0);

            self.selected_result =
                best_result_index(
                    &history[0].results,
                );

            self.restart_playback();
        }

        if is_key_pressed(KeyCode::PageUp) {
            self.select_previous_generation(history);
        }

        if is_key_pressed(KeyCode::PageDown) {
            self.select_next_generation(history);
        }

        let generation_index =
            self.selected_generation.unwrap();

        let results =
            &history[generation_index].results;

        if results.is_empty() {
            self.selected_result = None;
            return;
        }

        if self.selected_result.is_none() {
            self.selected_result =
                best_result_index(results);

            self.restart_playback();
        }

        if is_key_pressed(KeyCode::Left) {
            self.select_previous_result(
                results.len(),
            );
        }

        if is_key_pressed(KeyCode::Right) {
            self.select_next_result(
                results.len(),
            );
        }

        if is_key_pressed(KeyCode::B) {
            self.select_best_result(results);
        }

        if is_key_pressed(KeyCode::Space) {
            self.playing = !self.playing;
        }

        if is_key_pressed(KeyCode::R) {
            self.restart_playback();
        }

        if is_key_pressed(KeyCode::Up) {
            self.playback_speed =
                (self.playback_speed * 2.0)
                    .min(1000.0);
        }

        if is_key_pressed(KeyCode::Down) {
            self.playback_speed =
                (self.playback_speed / 2.0)
                    .max(1.0);
        }

        let result_index =
            self.selected_result.unwrap();

        let path_length =
            results[result_index]
                .simulation
                .path
                .len();

        if path_length == 0 {
            return;
        }

        if self.playback_index >= path_length {
            self.playback_index =
                path_length - 1;
        }

        if !self.playing {
            return;
        }

        self.playback_accumulator +=
            get_frame_time()
                * self.playback_speed;

        while self.playback_accumulator >= 1.0 {
            if self.playback_index + 1
                >= path_length
            {
                self.playing = false;
                self.playback_accumulator = 0.0;
                break;
            }

            self.playback_index += 1;
            self.playback_accumulator -= 1.0;
        }
    }

    fn select_previous_generation(
        &mut self,
        history: &[GenerationRecord],
    ) {
        let current =
            self.selected_generation.unwrap_or(0);

        let next =
            if current == 0 {
                history.len() - 1
            } else {
                current - 1
            };

        self.selected_generation =
            Some(next);

        self.selected_result =
            best_result_index(
                &history[next].results,
            );

        self.restart_playback();
    }

    fn select_next_generation(
        &mut self,
        history: &[GenerationRecord],
    ) {
        let current =
            self.selected_generation.unwrap_or(0);

        let next =
            (current + 1) % history.len();

        self.selected_generation =
            Some(next);

        self.selected_result =
            best_result_index(
                &history[next].results,
            );

        self.restart_playback();
    }

    fn select_previous_result(
        &mut self,
        result_count: usize,
    ) {
        let current =
            self.selected_result.unwrap_or(0);

        self.selected_result = Some(
            if current == 0 {
                result_count - 1
            } else {
                current - 1
            },
        );

        self.restart_playback();
    }

    fn select_next_result(
        &mut self,
        result_count: usize,
    ) {
        let current =
            self.selected_result.unwrap_or(0);

        self.selected_result =
            Some(
                (current + 1)
                    % result_count,
            );

        self.restart_playback();
    }

    fn select_best_result(
        &mut self,
        results: &[JobResult],
    ) {
        self.selected_result =
            best_result_index(results);

        self.restart_playback();
    }

    fn restart_playback(&mut self) {
        self.playback_index = 0;
        self.playback_accumulator = 0.0;
        self.playing = true;
    }
}

fn best_result_index(
    results: &[JobResult],
) -> Option<usize> {
    results
        .iter()
        .enumerate()
        .max_by(|(_, a), (_, b)| {
            a.fitness.total_cmp(&b.fitness)
        })
        .map(|(index, _)| index)
}