# FSR Sensor Characterization Experiment

This project determines and compares the value ranges of two batches of
Force Sensitive Resistor (FSR) sensors using an STM32 Black Pill
microcontroller. The experiment logs analog readings from 10 FSRs
connected to various GPIO pins and analyzes their behavior under
different applied forces.

------------------------------------------------------------------------

## \## Sensor Batch Comparison

### **1. Large-Diameter FSR (18.3 mm Short Tail)**

- **Product Link:**  
  https://www.aliexpress.com/item/1005004179560138.html?spm=a2g0o.productlist.main.3.2abd745bx4g5Qf&algo_pvid=62851c7d-c8f2-4dfd-b0a4-8640cacc2dda&algo_exp_id=62851c7d-c8f2-4dfd-b0a4-8640cacc2dda-2&pdp_ext_f=%7B%22order%22%3A%2222%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21LKR%21684.46%21684.46%21%21%211.98%211.98%21%4021010d9017653315653574763edf0b%2112000029375561128%21sea%21LK%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3Aef51c8d8%3Bm03_new_user%3A-29895&curPageLogUid=C0mXhUAEBzqL&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005004179560138%7C_p_origin_prod%3A

- **Sensing Range:** 0.2 N – 20 N  (0.02 kg – 2.0 kg)
- **Observed Serial Output Range:** **0 – 1005**

These sensors have a broader active area, making them more sensitive at
higher forces. The readings can climb close to the ADC maximum.

------------------------------------------------------------------------

### **2. Small-Diameter FSR (7.5 mm Short Tail)**

- **Product Link:**  
  https://www.daraz.lk/products/10kg-flexible-thin-film-resistor-type-pressure-force-sensor-diameter-75mm-i468452501-s2348987727.html?tradePath=omItm&dsource=share&laz_share_info=2324033570_0_100_313960_2324035570_null&laz_token=5967c58e0acac87d65eadcac756fa948&exlaz=e_Suk%2FkoKnCZHGip8qo24MCYMJi4p1oqLymUr0ZCz22CzCXvTKdNAtBRDjfkVq9rrTXDCmqmBVz2nYKBL%2Bg5j681syLq7qX%2BphSPdvZ0DPOq0%3D&sub_aff_id=social_share&sub_id2=2324033570&sub_id3=313960&sub_id6=CPI_EXLAZ

- **Sensing Range:** 0 – 10 kg  (0 N – 100 N)
- **Observed Serial Output Range:** **0 – 562**

The smaller sensing area produces lower ADC values for the same force
compared to the larger FSR. This sensor is connected to **PA6** in the
experiment.

------------------------------------------------------------------------

## Pin Mapping

    PA6 → Small 7.5 mm sensor  
    PA3 → Large 18.3 mm sensor (highlighted in logs)
    Other pins → Large-diameter FSRs

------------------------------------------------------------------------

## Serial Monitor Output (Full, Unmodified)

Below are the exact raw logs captured during the experiment.

### **Output Set 1 (PA6 highlighted)**

-   PA6 corresponds to **index 3** in each line
    (`PB1, PB0, PA7, PA6, ...`)

```{=html}
<!-- -->
```
    FSR Live: 0.09, 0.06, 0.08, **0.15**, 123.57, 0.34, 0.12, 158.66, 0.03, 0.08
    FSR Live: 0.10, 0.11, 0.10, **0.10**, 117.61, 0.34, 0.06, 157.68, 0.04, 0.12
    FSR Live: 0.09, 0.09, 0.03, **0.12**, 113.18, 0.30, 0.11, 159.06, 0.10, 0.06
    FSR Live: 0.09, 0.11, 0.00, **0.15**, 109.69, 0.19, 0.12, 157.19, 0.11, 0.14
    FSR Live: 0.11, 0.10, 0.08, **0.09**, 107.11, 0.27, 0.04, 157.81, 0.10, 0.09
    FSR Live: 1.61, 1.73, 1.69, **358.86**, 143.55, 2.00, 1.56, 156.91, 1.59, 1.70
    FSR Live: 1.67, 1.67, 1.60, **357.76**, 143.63, 1.95, 1.59, 156.86, 1.73, 1.75
    FSR Live: 1.77, 1.66, 1.67, **361.05**, 143.70, 1.94, 1.56, 155.64, 1.71, 1.83
    FSR Live: 1.71, 1.65, 1.66, **362.89**, 144.10, 1.88, 1.61, 157.18, 1.75, 1.73
    FSR Live: 1.67, 1.67, 1.54, **360.44**, 144.38, 1.90, 1.66, 158.04, 1.75, 1.77
    FSR Live: 1.66, 1.66, 1.70, **362.33**, 144.43, 1.91, 1.65, 159.75, 1.65, 1.64
    FSR Live: 1.92, 1.90, 1.89, **405.23**, 145.49, 2.04, 1.80, 160.41, 1.83, 1.99
    FSR Live: 1.92, 1.94, 1.90, **415.69**, 147.05, 2.15, 1.75, 160.40, 1.90, 2.03
    FSR Live: 2.11, 2.03, 2.14, **467.14**, 149.24, 2.36, 2.03, 159.04, 2.24, 2.19
    FSR Live: 2.53, 2.51, 2.50, **547.79**, 153.69, 2.70, 2.46, 159.24, 2.61, 2.55
    FSR Live: 2.56, 2.66, 2.60, **562.55**, 157.29, 2.88, 2.49, 158.84, 2.60, 2.66
    FSR Live: 2.51, 2.51, 2.49, **548.71**, 158.85, 2.85, 2.39, 157.88, 2.39, 2.58
    FSR Live: 2.54, 2.48, 2.35, **540.19**, 159.19, 2.69, 2.39, 158.61, 2.45, 2.60
    FSR Live: 2.35, 2.38, 2.44, **542.99**, 159.36, 2.78, 2.35, 157.54, 2.39, 2.59

------------------------------------------------------------------------

### **Output Set 2 (PA4 highlighted)**

-   PA4 corresponds to **index 5**

```{=html}
<!-- -->
```
    FSR Live: 4.19, 4.11, 4.04, 3.96, 130.96, **1005.04**, 4.24, 153.55, 4.01, 4.09
    FSR Live: 4.10, 4.11, 3.99, 4.01, 131.54, **1005.06**, 4.26, 155.38, 4.18, 4.10
    FSR Live: 4.16, 4.03, 4.13, 3.96, 132.13, **1005.11**, 4.26, 155.73, 4.03, 4.00
    FSR Live: 4.16, 4.11, 4.05, 4.04, 132.43, **1005.14**, 4.26, 155.23, 4.03, 3.99
    FSR Live: 4.04, 4.03, 4.00, 4.07, 132.89, **1004.89**, 4.30, 156.27, 4.11, 4.10
    FSR Live: 4.03, 4.06, 3.99, 4.03, 133.21, **1005.10**, 4.28, 157.63, 3.93, 4.13
    FSR Live: 4.06, 4.15, 4.04, 4.05, 133.96, **1004.86**, 4.28, 160.30, 4.07, 4.21
    FSR Live: 4.23, 4.11, 4.07, 4.01, 133.75, **1004.80**, 4.43, 161.58, 4.13, 4.21
    FSR Live: 4.10, 4.05, 3.98, 3.96, 132.48, **974.14**, 4.15, 163.11, 4.01, 3.91
    FSR Live: 0.06, 0.11, 0.10, 0.03, 119.15, **0.10**, 0.16, 158.01, 0.08, 0.08
    FSR Live: 0.06, 0.04, 0.03, 0.12, 108.93, **0.11**, 0.09, 156.02, 0.06, 0.16
    FSR Live: 0.04, 0.09, 0.05, 0.10, 102.14, **0.16**, 0.00, 152.99, 0.04, 0.12
    FSR Live: 0.06, 0.08, 0.05, 0.08, 97.66, **0.08**, 0.15, 153.49, 0.11, 0.15
    FSR Live: 0.11, 0.08, 0.03, 0.11, 94.50, **0.11**, 0.09, 153.45, 0.06, 0.10

------------------------------------------------------------------------

## STM32 Code Used

(Full unmodified code included exactly as provided.)

    #include <Arduino.h>

    #define NUM_SENSORS 10

    uint8_t fsrPins[NUM_SENSORS] = {
      PB1, PB0,
      PA7, PA6, PA5, PA4, PA3, PA2, PA1, PA0
    };

    const int samples = 80;
    const int delay_ms = 3;
    const float threshold = 15.0;
    const int stableCyclesNeeded = 5;

    float prevMean[NUM_SENSORS] = {0};
    float savedData[NUM_SENSORS] = {0};

    int stableCounter = 0;
    bool hasSaved = false;

    void setup() {
      Serial.begin(115115200);
      delay(500);

      for (int i = 0; i < NUM_SENSORS; i++) {
        pinMode(fsrPins[i], INPUT_ANALOG);
      }

      Serial.println("FSR Auto-Save System Ready...");
    }

    void loop() {

      float meanVal[NUM_SENSORS] = {0};

      for (int i = 0; i < samples; i++) {
        for (int s = 0; s < NUM_SENSORS; s++) {
          meanVal[s] += analogRead(fsrPins[s]);
        }
        delay(delay_ms);
      }

      for (int s = 0; s < NUM_SENSORS; s++) {
        meanVal[s] /= samples;
      }

      bool allStable = true;

      for (int s = 0; s < NUM_SENSORS; s++) {
        float delta = fabs(meanVal[s] - prevMean[s]);
        if (delta > threshold) {
          allStable = false;
        }
      }

      if (allStable) {
        stableCounter++;
      } else {
        stableCounter = 0;
        hasSaved = false;
      }

      if (stableCounter >= stableCyclesNeeded && !hasSaved) {
        for (int s = 0; s < NUM_SENSORS; s++) {
          savedData[s] = meanVal[s];
        }

        Serial.println("=====================================");
        Serial.println("STABLE → DATA SAVED");
        Serial.print("FSR Snapshot: ");

        for (int s = 0; s < NUM_SENSORS; s++) {
          Serial.print(savedData[s], 2);
          if (s < NUM_SENSORS - 1) Serial.print(", ");
        }
        Serial.println();
        Serial.println("=====================================");

        hasSaved = true;
      }

      Serial.print("FSR Live: ");
      for (int s = 0; s < NUM_SENSORS; s++) {
        Serial.print(meanVal[s], 2);
        if (s < NUM_SENSORS - 1) Serial.print(", ");
      }
      Serial.println();

      for (int s = 0; s < NUM_SENSORS; s++) {
        prevMean[s] = meanVal[s];
      }

      delay(200);
    }

------------------------------------------------------------------------

## Summary

This experiment compares two FSR batches by analyzing their ADC output
under load.\
- The **7.5 mm sensor (PA6)** shows readings up to \~560.\
- The **18.3 mm sensors (including PA4)** reach values close to 1005.\
- The difference reflects sensor area, sensitivity, and force
distribution.

------------------------------------------------------------------------
