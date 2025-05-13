### Optimal Order Selection Problem
##### This is a challange was proposed by Mercado Livre in [SBPO 2025](https://sbpo2025.galoa.com.br/sbpo-2025/page/5407-home)
---
### Context
This challenge simulates a real-world logistics situation faced by Mercado Livre: once a customer places an order, the items must be picked from the warehouse. Picking items one order at a time is inefficient. Instead, selecting a group of orders — called a wave — allows workers to benefit from item proximity in the warehouse

### Objective

Select a subset of orders (a **wave**) and a subset of **aisles** (locations for picking items) to **maximize the productivity** of the picking process.

**Objective function:**

```
Total number of items to pick / Number of aisles used
```

---

### Constraints

To be considered a **valid wave** (subset `O'` of orders), the following constraints must be satisfied:

1. **Wave size constraints:**
```math
∑_{o ∈ O'} ∑_{i ∈ I_o} u_{oi} ≥ LB
```
```math
∑_{o ∈ O'} ∑_{i ∈ I_o} u_{oi} ≤ UB
```

2. **Aisle capacity constraint:**
```math
∑_{o ∈ O'} u_{oi} ≤ ∑_{a ∈ A'} u_{ai}, ∀ i ∈ I_o
```

Where:
- `u_{oi}` = units of item `i` in order `o`
- `u_{ai}` = units of item `i` available in aisle `a`
- `LB` and `UB` are the lower and upper bounds for wave size (total units)

---

### Key Definitions

- **Item**: A product available in the warehouse.
- **Order**: A list of items requested by a customer, with quantities.
- **Backlog**: Set of pending (unprocessed) orders.
- **Wave**: Subset of orders selected to be picked together.
- **Aisle**: Pathways between warehouse shelves where items are stored.

---

### Input/Output Format

#### Input File Includes:
- Number of orders, items, and aisles
- Items requested per order
- Items available per aisle
- Lower and upper bounds for wave size

#### Output File Must Include:
- Indices of selected orders (wave)
- Indices of selected aisles