## Option 1: Terminate Instance on Weekends

### Summary

Terminate the AWS EC2 instance on weekends to save on compute costs, while managing backup and restoration of the system using AWS AMIs and snapshots.

### Cost Analysis

#### Same VPC or Different VPC in the Same Region

- **Instance Cost Savings**: 
  - \( 60 \text{ hours/weekend} \times \$1.212 \text{ per hour} = \$72.72 \) per weekend
  - Monthly savings: \$290.88

- **Snapshot Cost (2 days per weekend)**:
  - \( 450 \text{ GB} \times \$0.05 \text{ per GB-month} \times \frac{2}{30} = \$1.50 \)
  - Monthly snapshot cost: \$6

- **Total Monthly Savings**: \$284.88

#### Different Region

- **Instance Cost Savings**: 
  - \( 60 \text{ hours/weekend} \times \$1.212 \text{ per hour} = \$72.72 \) per weekend
  - Monthly savings: \$290.88

- **Snapshot Cost (2 days per weekend)**:
  - \( 450 \text{ GB} \times \$0.05 \text{ per GB-month} \times \frac{2}{30} = \$1.50 \)
  - Monthly snapshot cost: \$6

- **Data Transfer Cost (one-time)**:
  - \( 450 \text{ GB} \times \$0.02 \text{ per GB} = \$9 \)

- **Total Monthly Savings for the First Month**: \$275.88
- **Total Monthly Savings for Subsequent Months**: \$284.88

---

## Option 2: Power Off/On Instance on Weekends

### Summary

Power off the AWS EC2 instance on weekends to save on compute costs, while retaining the instance and its storage for quick resumption on Monday mornings.

### Cost Analysis

#### Same VPC or Different VPC in the Same Region

- **Instance Cost for Full Month**: 
  - \( 24 \text{ hours/day} \times 30 \text{ days} \times \$1.212 \text{ per hour} = \$872.16 \)

- **Instance Cost Savings (Weekends)**:
  - \( 8 \text{ hours/day} \times 2 \text{ days} \times \$1.212 \text{ per hour} = \$19.39 \) per weekend
  - Monthly savings: \( \$19.39 \times 4 \text{ weekends} = \$77.56 \)

- **EBS Volume Storage Cost for Full Month**:
  - \( 450 \text{ GB} \times \$0.10 \text{ per GB-month} = \$45 \)

- **EBS Volume Storage Cost (Weekends Only)**:
  - \( 450 \text{ GB} \times \$0.10 \text{ per GB-month} \times \frac{2}{30} = \$3 \)
  - Monthly storage cost: \( \$3 \times 4 = \$12 \)

- **Total Monthly Cost**:
  - \( \$872.16 \text{ (Instance)} + \$45 \text{ (EBS Storage)} = \$917.16 \)

- **Total Monthly Savings**: \( \$917.16 \text{ (Total Monthly Cost)} - \$77.56 \text{ (Instance Savings)} - \$12 \text{ (EBS Storage for Weekends)} = \$827.60 \)

#### Different Region

- **Instance Cost for Full Month**: 
  - \( 24 \text{ hours/day} \times 30 \text{ days} \times \$1.212 \text{ per hour} = \$872.16 \)

- **Instance Cost Savings (Weekends)**:
  - \( 8 \text{ hours/day} \times 2 \text{ days} \times \$1.212 \text{ per hour} = \$19.39 \) per weekend
  - Monthly savings: \( \$19.39 \times 4 \text{ weekends} = \$77.56 \)

- **EBS Volume Storage Cost for Full Month**:
  - \( 450 \text{ GB} \times \$0.10 \text{ per GB-month} = \$45 \)

- **EBS Volume Storage Cost (Weekends Only)**:
  - \( 450 \text{ GB} \times \$0.10 \text{ per GB-month} \times \frac{2}{30} = \$3 \)
  - Monthly storage cost: \( \$3 \times 4 = \$12 \)

- **Total Monthly Cost**:
  - \( \$872.16 \text{ (Instance)} + \$45 \text{ (EBS Storage)} = \$917.16 \)

- **Total Monthly Savings**: \( \$917.16 \text{ (Total Monthly Cost)} - \$77.56 \text{ (Instance Savings)} - \$12 \text{ (EBS Storage for Weekends)} = \$827.60 \)

---

### Conclusion

- **Option 1 (Terminate Instance)**: Provides higher monthly savings due to lower ongoing storage costs, with initial data transfer costs in different regions.
  
- **Option 2 (Power Off/On)**: Offers consistent monthly savings but retains ongoing storage costs, which are incurred even when the instance is powered off.
