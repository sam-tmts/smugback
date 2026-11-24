# Architecture

How SmugBack is built, at two levels of the [C4 model](https://c4model.com/):
**context** (the system and the people and systems around it) and **containers** (the
deployable parts and how they talk). Diagrams are written in Mermaid so GitHub renders
them. Keep this current through CRs.

## System context

The owner runs SmugBack on their own computer. It reads their account from SmugMug's
API and writes copies of their photos and videos to a local folder. It never changes
anything on SmugMug.

```mermaid
flowchart LR
    owner([Owner]) -- runs --> smugback[SmugBack<br/>command-line tool]
    smugback -- reads albums, photos and videos --> smugmug[(SmugMug API)]
    smugback -- writes backups --> disk[(Local folder)]
```

## Containers

One container: the `smugback` Python package (`src/smugback/`), run as a command. Its
entry point is `smugback.cli:main`. There is no server or database.
