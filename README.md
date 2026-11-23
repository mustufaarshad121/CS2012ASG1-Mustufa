# CS2012ASG1-Mustufa

# FinPay — Transaction Management & Audit System (CS2012 Assignment 1)

## Overview
FinPay is a modular Python desktop application for ingesting, filtering, auditing, and exporting financial transaction ledgers (`.csv` and `.json`).

## Architecture & Custom Data Structures (`backend.py`)
* **OOP & Polymorphism:** Abstract `Transaction` and `FileLoader` base classes with `CreditTransaction` (`+amount`), `DebitTransaction` (`-amount`), `CSVLoader`, and `JSONLoader`.
* **FIFO `IngestionQueue`:** Buffers validated transaction objects during file ingestion.
* **LIFO `FilterHistoryStack`:** Tracks previous `(City, Date, Type)` filter states so users can undo filter changes step-by-step.
* **Singly Linked List `ExportAuditLinkedList`:** Records chronological `(timestamp, action, count, net_impact)` audit events (`LOAD`, `FILTER`, `REVERT`, `CLEAR`, `EXPORT`).

## Design Note
* **`clear_filters()` Undo Support:** Clicking **Clear Filters** pushes the active non-default filter state onto `FilterHistoryStack` before resetting to `("All", "All", "All")`, allowing **Revert Filter** to undo a clear action as well.

## How to Run
```bash
python UI_Starter_Code.py