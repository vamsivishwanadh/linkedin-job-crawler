from __future__ import annotations

from typing import Any

from apify_client import ApifyClient

from src.config import ApifySettings, SearchSettings


def build_actor_input(apify: ApifySettings, search: SearchSettings) -> dict[str, Any]:
    return {
        "titles": search.titles,
        "locations": search.locations,
        "rows": apify.max_rows_per_search,
        "publishedAt": apify.published_at,
        "easyApply": search.easy_apply,
        "under10Applicants": search.under_10_applicants,
        "workTypes": search.work_types,
        "contractTypes": search.contract_types,
        "experienceLevels": search.experience_levels,
        "companyProfile": apify.company_profile,
        "enrichCompany": apify.enrich_company,
    }


def fetch_jobs_from_dataset(token: str, dataset_id: str) -> list[dict[str, Any]]:
    client = ApifyClient(token)
    return list(client.dataset(dataset_id).iterate_items())


def fetch_jobs_from_run(token: str, run_id: str) -> list[dict[str, Any]]:
    client = ApifyClient(token)
    run = client.run(run_id).get()
    return fetch_jobs_from_dataset(token, run.default_dataset_id)


def fetch_jobs(token: str, apify: ApifySettings, search: SearchSettings) -> list[dict[str, Any]]:
    client = ApifyClient(token)
    run_input = build_actor_input(apify, search)
    run = client.actor(apify.actor_id).call(run_input=run_input)
    if run is None:
        raise RuntimeError("Apify actor run did not return a run object.")
    return fetch_jobs_from_dataset(token, run.default_dataset_id)
