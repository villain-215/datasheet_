import os
import pandas as pd
from src.extractor import extract_datasheets
from src.evaluator import run_evaluation
import src.config as config

def main():
    print("====================================================")
    print("        Datasheet Parameter Extractor Pipeline      ")
    print("====================================================")
    
    # 1. API Key check bypassed (Local Programmatic Extraction)
    pass
        
    # 2. Collect PDF files from dataset
    dataset_dir = config.DATASET_DIR
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory not found at: {dataset_dir}")
        return
        
    pdf_files = [
        os.path.join(dataset_dir, f) 
        for f in os.listdir(dataset_dir) 
        if f.lower().endswith(".pdf")
    ]
    
    if not pdf_files:
        print(f"No PDF files found in {dataset_dir}")
        return
        
    # For testing: process only the first 3 files
    # pdf_files = pdf_files[:3]
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    # 3. Execute extraction via VLM by processing files sequentially
    try:
        results = extract_datasheets(pdf_files)
    except Exception as e:
        print(f"Error during VLM extraction: {e}")
        return
        
    if not results:
        print("No results returned from extraction.")
        return

        
    # 4. Save results to DataFrame
    df = pd.DataFrame(results)
    
    # Define exact columns and order required by the ground truth sheet
    col_mapping = {
        "filename": "Filename",
        "part_number": "Part Number",
        "min_operating_temp_c": "Minimum Operating Temperature(°C)",
        "max_operating_temp_c": "Maximum Operating Temperature (°C)",
        "max_length_mm": "Maximum Length (mm)",
        "max_width_mm": "Maximum Width (mm)",
        "max_height_mm": "Maximum Height (mm)",
        "pin_number": "PIN Number",
        "io_if_a": "I_O、I_F (A)",
        "vf_v": "V_F(Forward Voltage) (V)",
        "vrrm_v": "V_RRM(Peak Repetitive Reverse Voltage) (V)",
        "ir_a": "I_R(Reverse Current) " # Trailing space
    }
    
    # Ensure all columns exist in df
    for raw_col in col_mapping.keys():
        if raw_col not in df.columns:
            df[raw_col] = None
            
    # Rearrange and rename columns
    df = df[list(col_mapping.keys())]
    df.rename(columns=col_mapping, inplace=True)
    
    # Save to CSV and JSON (Excel skipped as requested)
    output_csv = config.DEFAULT_OUTPUT_CSV
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nExtraction completed. CSV output saved to: {output_csv}")
    
    output_json = config.DEFAULT_OUTPUT_JSON
    import json
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Extraction completed. JSON output saved to: {output_json}")
    
    # 5. Run accuracy evaluation automatically using CSV
    print("\nRunning accuracy evaluation against ground truth...")
    run_evaluation(output_csv, config.GROUND_TRUTH_EXCEL)

if __name__ == "__main__":
    main()
