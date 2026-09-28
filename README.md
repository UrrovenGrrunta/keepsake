# Keepsake

Keepsake is a local-first personal journal written in Python. It is intended to keep journal entries, people, directed relationships, events, photos and, later, music in one private timeline.

The project is in early development. The domain model and SQLite persistence layer are implemented; the next milestone is a minimal application bootstrap before GUI work begins.

## Principles

- Personal data stays on the user's device and is never committed to Git.
- An `Event` describes what happened; a `JournalEntry` describes how it was recorded or experienced.
- Journal entries preserve an ordered sequence of blocks, such as text → photo → text.
- Relationships are directed: A → B and B → A have independent roles and sentiments.
- People are database records represented by one universal `Person` model.
- The project favours small, useful abstractions over enterprise boilerplate.

## Current status

Implemented:

- domain models for people, relationships, events, photos and journal entries;
- text and photo journal blocks with stable ordering;
- SQLite schema creation and small compatibility migrations;
- repositories for all current domain entities;
- foreign-key rules, transactional writes and rollback behaviour;
- integration coverage for saving, reopening and loading local data;
- 39 passing tests at the current roadmap snapshot.

Planned next:

1. initialise `data/keepsake.db` from the application entry point;
2. centralise local data and photo paths;
3. implement local photo import;
4. create a minimal portrait-first Kivy/KivyMD application shell;
5. build the journal, history, people, profile and About screens;
6. add Spotify integration and visual polish later.

See the detailed [project roadmap](docs/roadmap.md) for completed work, upcoming tasks and decision points.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/UrrovenGrrunta/keepsake.git
cd keepsake
uv sync --dev
```

Run the application:

```bash
uv run keepsake
```

Run the test suite:

```bash
uv run pytest
```

## Project structure

```text
src/keepsake/
├── domain/       # Domain models and invariants
└── storage/      # SQLite connection, schema and repositories
tests/            # Unit and integration tests
docs/             # Roadmap and project documentation
data/             # Local database and photos; ignored by Git
```

## Planned stack

- Python 3.12
- uv
- SQLite
- Kivy/KivyMD
- Spotify Web API

## Privacy

Keepsake is designed as a local application. The database and imported photos belong under `data/`, which is ignored by Git. Cloud accounts and synchronisation are deliberately outside the current scope.