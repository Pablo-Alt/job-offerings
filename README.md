# Job Offerings

## Folder structure

```
job-offerings/
├── README.md
├── src/
│   ├── analyze_linkedin_jobs.py
│   └── job_titles.yaml
├── tests/
│   └── fixtures/
│       └── valid_job_offerings_input.json
└── data/
    └── inputs/
        └── {linkedin_jobs_search_name}.json
```

Aquí está el contenido del repositorio, need-to-know basis:
- The implementation lies in the `src/analyze_linkedin_jobs.py` script
- The desired **list of job titles** (used for grouping the output links document) lies in the `src/job_titles.yaml` configuration file
- The fake sample input json (used to test the implementation) is the `tests/fixtures/valid_job_offerings_input.json` file
- The **real input json** (downloaded from a linkedin search with the scraper.net extension) the user wants to process **must be placed** inside the `data/inputs/` folder

## Execution examples (from the root directory)

Test with fixture input:

```bash
python src/analyze_linkedin_jobs.py tests/fixtures/valid_job_offerings_input.json
```

Execute with real input:


```bash
python src/analyze_linkedin_jobs.py data/inputs/{job_offerings_file_name}.json
```