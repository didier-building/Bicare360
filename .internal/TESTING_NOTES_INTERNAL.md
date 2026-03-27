# INTERNAL USE ONLY - TESTING ACCESS NOTES

This file is for internal QA/development workflows only.
Do not expose this file in demos, screenshots, or external documentation.

## Rules
- Never show test usernames/passwords on public-facing UI pages.
- Keep testing credentials in secure internal channels only.
- Rotate any shared test accounts before external demos.
- Use least-privilege accounts for validation flows.

## Current Practice
- Use local setup scripts under `backend/` to provision test users in development.
- Keep `.env` secrets and any credential material out of versioned public docs.
- Before release, verify no credential text appears in frontend pages.

## Pre-release Check
- Confirm `LoginSelectionPage` and `LoginPage` contain no credential hints.
- Confirm root-level guides are marked `DEV ONLY` when they include test access details.
