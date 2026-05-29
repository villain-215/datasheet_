from pydantic import BaseModel, Field
from typing import Optional

class DatasheetInfo(BaseModel):
    filename: str = Field(
        description="The original filename of the datasheet. E.g., 'BAS16.pdf'."
    )
    part_number: Optional[str] = Field(
        None, 
        description="Part number of the device. Extract from the document header or text. If not found, infer from filename (e.g., 'BAS16')."
    )
    min_operating_temp_c: Optional[str] = Field(
        None, 
        description="Minimum operating temperature or storage/junction temperature in °C. Output just the numerical value (e.g. -55 or -65). Look carefully at the 'Temperature Range' specification."
    )
    max_operating_temp_c: Optional[str] = Field(
        None, 
        description="Maximum operating or junction temperature in °C. Output just the numerical value (e.g. 125 or 150). Note: Do not confuse it with storage temperature if operating temp is specified separately, otherwise use the maximum junction temperature."
    )
    max_length_mm: Optional[str] = Field(
        None, 
        description="Maximum overall length in mm. This refers to the total package length including pins/leads (often labeled as D, E, L, or Z in package outline drawings). Cross-reference the package outline drawing labels with the dimension table and extract the MAX value. Output only the numerical value in mm. E.g., 3.86."
    )
    max_width_mm: Optional[str] = Field(
        None, 
        description="Maximum overall width in mm. This refers to the total package width including pins/leads (often labeled as E, E1, HE, b, etc.). Cross-reference the package outline drawing labels with the dimension table and extract the MAX value. Output only the numerical value in mm. E.g., 1.8."
    )
    max_height_mm: Optional[str] = Field(
        None, 
        description="Maximum overall height in mm. This refers to the total height of the package (often labeled as A or A1 in package outline drawings). Cross-reference the package outline drawing labels with the dimension table and extract the MAX value. Output only the numerical value in mm. E.g., 1.35."
    )
    pin_number: Optional[str] = Field(
        None, 
        description="Number of physical pins or terminals of the package. Output as a numerical integer. E.g., 2, 3, or 4."
    )
    io_if_a: Optional[str] = Field(
        None, 
        description="Average rectified output current or forward current (Io or If) in A. Convert to Amperes if in mA (e.g. 150mA is 0.15). Do not include unit, just output the number (e.g., 0.15 or 0.75). Keep conditions in text if needed, but prioritize outputting the main current value in A."
    )
    vf_v: Optional[str] = Field(
        None, 
        description="Forward voltage (V_F) in V. You MUST extract ALL forward voltage conditions and values listed in the electrical characteristics table, and join them together with the ideographic comma '、' (U+3001). Format: 'voltage @current'. E.g., '0.715 @1mA、0.855 @10mA、1 @50mA、1.25 @150mA'. Do not use English commas or semicolons."
    )
    vrrm_v: Optional[str] = Field(
        None, 
        description="Peak repetitive reverse voltage (V_RRM) in V. Output just the numerical value. E.g., 75, 100, or 1000."
    )
    ir_a: Optional[str] = Field(
        None, 
        description="Reverse current (I_R). You MUST extract ALL reverse current conditions and values listed in the electrical characteristics table, and join them together with the ideographic comma '、' (U+3001). Format: 'current @voltage' or 'current @voltage, temp'. E.g., '2.5uA @75V、25nA @20V' or '10uA @150V, 25°C、2mA @150V, 125°C'. Keep units like uA, nA, mA."
    )

class DatasheetList(BaseModel):
    datasheets: list[DatasheetInfo]
