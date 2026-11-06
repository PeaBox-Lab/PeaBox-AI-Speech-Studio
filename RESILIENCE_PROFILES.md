# Resilience Profiles Guide

## Stored settings
Attempts, delay, backoff, timeout, failure threshold, and recovery duration. No credentials.

## Lifecycle
Draft → In Review → Approved → Active. Review may request changes. Profiles can be archived.

## Separation
Creator cannot approve their own profile. Actor names are local labels, not authentication.

## Activation
One Active profile per backend. Activating another returns the prior one to Approved.

## Audit
All lifecycle actions are appended to the profile audit history.
