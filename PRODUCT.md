# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

delegated: Vite + React (chosen for fast, modern component development, ideal for a rich UI dashboard experience)

## Users

Personal project. The intended audience includes the creator, reviewers, or portfolio visitors exploring the platform's capabilities.

## Product Purpose

To demonstrate a robust financial analytics platform that handles data ingestion, machine-learning-based forecasting, and interactive data exploration in a single system.

## Positioning

A seamless hybrid of natural language querying (AI) and rigid deterministic KPIs.

## Operating Context

Local development environment and portfolio showcase. It uses a self-contained, pre-generated synthetic financial dataset to ensure immediately verifiable results without external dependencies.

## Capabilities and Constraints

- Natural language to SQL query engine powered by Gemini, featuring strict safety guards against destructive operations.
- 100% deterministic KPI module calculating DSO, Aging Buckets, Cash Runway, and Cash Flow using SQLite and pandas.
- Numpy-backed linear regression forecasting that automatically handles partial data exclusions.
- Completely isolated modular architecture (data, query_engine, kpi, forecasting, dashboard).

## Evidence on Hand

- A populated local SQLite database (`finsight.db`).
- Fully tested and working Python backend modules for AI querying, KPI reporting, and trend forecasting.
