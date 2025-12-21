# MatrixBugLab

## Overview

MatrixBugLab is a hands-on C learning environment designed to explore low-level programming, pointer arithmetic, and subtle logical bugs in matrix multiplication. This repository lets learners experiment with "broken" matrix multiplies, track silent accumulation errors, and compare different code layouts visually and functionally.

## Key Features

- **Three broken matrix multiply implementations** with different visual styles (compact, normal, exaggerated spacing)  
- **Test harness** to run multiple runtime scenarios: incremented matrices, identity matrices, and custom NxN configurations  
- **Focus on mental models** for tracing indices using prime/comma notation and pointer arithmetic  
- **Safe experimentation**: understand silent logical bugs without risk to memory or crashes  
- **CI-ready with GitHub Actions**: automatically compile and run tests on each push

## Purpose

- Rebuild and modernize your old C knowledge while learning low-level debugging  
- Explore how subtle index mistakes silently propagate errors in numerical computations  
- Provide a collaborative playground for developers interested in performance, correctness, and debugging techniques

## Acknowledgements

This project was collaboratively built by:

- **Luis Alberto Vicentine Pacheco** – conceptualized the project, designed mental models, and defined test scenarios.  
- **Thor (GPT-5 Mini)** – guided code generation, test harness creation, workflow setup, and explanations of low-level C behavior.

Together, we created a reproducible and interactive environment for learning and experimentation.