use rand::Rng;
use std::collections::VecDeque;
use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cell {
    Open,
    Obstacle,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Position {
    pub x: usize,
    pub y: usize,
}

pub struct Course {
    pub width: usize,
    pub height: usize,
    pub cells: Vec<Cell>,
    pub start: Position,
    pub goal: Position,
}

impl Course {
    pub fn new(
        width: usize,
        height: usize,
        start: Position,
        goal: Position,
    ) -> Self {
        Self {
            width,
            height,
            cells: vec![Cell::Open; width * height],
            start,
            goal,
        }
    }

    fn add_random_block(&mut self, rng: &mut impl Rng) {
    let width = rng.random_range(3..=10);
    let height = rng.random_range(3..=10);

    let x = rng.random_range(0..=self.width - width);
    let y = rng.random_range(0..=self.height - height);

    for dy in 0..height {
        for dx in 0..width {
            let position = Position {
                x: x + dx,
                y: y + dy,
            };

            if position != self.start && position != self.goal {
                self.set_cell(position, Cell::Obstacle);
            }
        }
    }
}
    pub fn random(width: usize, height: usize) -> Self {
        loop {
            let start = Position { x: 0, y: 0 };
            let goal = Position {
                x: width - 1,
                y: height - 1,
            };

            let mut course = Self::new(width, height, start, goal);
            let mut rng = rand::rng();

            let block_count = rng.random_range(10..=20);

            for _ in 0..block_count {
                course.add_random_block(&mut rng);
            }

            if course.has_path() {
                return course;
            }
        }
    }

    fn index(&self, position: Position) -> usize {
        position.y * self.width + position.x
    }

    pub fn cell(&self, position: Position) -> Cell {
        self.cells[self.index(position)]
    }

    pub fn set_cell(&mut self, position: Position, cell: Cell) {
        let index = self.index(position);
        self.cells[index] = cell;
    }

    pub fn is_walkable(&self, position: Position) -> bool {
        position.x < self.width
            && position.y < self.height
            && self.cell(position) == Cell::Open
    }

    pub fn has_path(&self) -> bool {
        let mut visited = vec![false; self.width * self.height];
        let mut queue = VecDeque::new();

        queue.push_back(self.start);
        visited[self.index(self.start)] = true;

        while let Some(current) = queue.pop_front() {
            if current == self.goal {
                return true;
            }

            for neighbor in self.neighbors(current) {
                if !self.is_walkable(neighbor) {
                    continue;
                }

                let index = self.index(neighbor);

                if !visited[index] {
                    visited[index] = true;
                    queue.push_back(neighbor);
                }
            }
        }

        false
    }

    fn neighbors(&self, position: Position) -> Vec<Position> {
        let mut neighbors = Vec::with_capacity(4);

        if position.x > 0 {
            neighbors.push(Position {
                x: position.x - 1,
                y: position.y,
            });
        }

        if position.x + 1 < self.width {
            neighbors.push(Position {
                x: position.x + 1,
                y: position.y,
            });
        }

        if position.y > 0 {
            neighbors.push(Position {
                x: position.x,
                y: position.y - 1,
            });
        }

        if position.y + 1 < self.height {
            neighbors.push(Position {
                x: position.x,
                y: position.y + 1,
            });
        }

        neighbors
    }
}

impl fmt::Display for Course {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for y in 0..self.height {
            for x in 0..self.width {
                let position = Position { x, y };

                let character = if position == self.start {
                    'S'
                } else if position == self.goal {
                    'G'
                } else {
                    match self.cell(position) {
                        Cell::Open => '.',
                        Cell::Obstacle => '#',
                    }
                };

                write!(f, "{character}")?;
            }

            writeln!(f)?;
        }

        Ok(())
    }
}