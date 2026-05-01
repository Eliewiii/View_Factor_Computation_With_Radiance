# Radiance-VF: High-Performance View Factor Computation

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Radiance](https://img.shields.io/badge/Radiance-5.4-lightgrey?style=for-the-badge)
![Algorithm](https://img.shields.io/badge/Algorithm-Optimization-red?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**Radiance-VF** is a specialized Python engine for computing the **View Factor (VF) matrix** of complex 3D scenes. Designed specifically for district-scale building energy models, it handles intricate geometries (including surfaces with holes and fenestrations) and optimizes the computational bottleneck of radiative exchange.

---
> **💡 Key Innovation**
>
> Implements a **Minimum View Factor (Min-VF) Criterion** to intelligently prune negligible geometric interactions, allowing for sparse matrix generation and drastically reduced execution times.
---

## 🚀 Key Features

### 1. Advanced Geometric Processing
*   **Hole & Fenestration Support:** Correctly handles building surfaces with complex apertures (windows/doors), ensuring area and normal computations are numerically accurate for radiative balance.
*   **Automated Scene Generation:** Programmatically generates Radiance-compliant input files and octrees from surface datasets.

### 2. High-Performance Execution
*   **Parallel Processing:** Orchestrates the `Radiance` ray-tracing engine across multiple CPU cores to handle massive view-factor matrices (verified for 20000+ surfaces).

### 3. Algorithmic Pruning (Min-VF Criterion)
*   **Complexity Reduction:** Uses a threshold-based technique to skip the computation of insignificant view factors.

## 🛠️ Prerequisites

*   **Radiance:** Must be installed on the system.
*   **Environment Setup:** Add the Radiance `bin` folder to your `PATH` and set the `RAYPATH` to the `lib` folder.
*   **Note for Windows Users:** High CPU usage by Antivirus software (Windows Defender) is common during Radiance execution. It is recommended to add a process exclusion for the Radiance binaries to prevent performance degradation.

## 📂 Project Structure

* `src/`: Core Python source code for parallelizing Radiance calls and VF matrix assembly.
* `tests/`: Unit tests for geometric accuracy, area conservation, and normal vector consistency.

---

## 🎓 Context & Credits

**Author:** Elie Medioni, Ph.D.

This project was developed to resolve the "computational bottleneck" of district-scale radiative modeling. It serves as a specialized geometric engine for the **[BUA Framework](https://github.com/Eliewiii/BUA)** and the **[LWR-EPCoupling](https://github.com/Eliewiii/EP_LWR_coupled_simulation)** system.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
