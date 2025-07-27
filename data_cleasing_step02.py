import pandas as pd

# โหลดไฟล์ CSV
df = pd.read_csv("filtered_tcas_cleaned_fillbyhand.csv")

# ดึงเฉพาะบางคอลัมน์
selected_columns = ['มหาวิทยาลัย', 'ค่าใช้จ่าย', 'ชื่อหลักสูตร', 'ชื่อหลักสูตรภาษาอังกฤษ']
new_df = df[selected_columns].copy()

# แปลงค่าใช้จ่ายให้เป็นตัวเลข (ลบ , และแปลงเป็น float)
new_df['ค่าใช้จ่าย'] = (
    new_df['ค่าใช้จ่าย']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.extract(r'(\d+(?:\.\d+)?)')
    .astype(float)
)

# หากค่าใช้จ่าย > 90000 ให้หาร 8
new_df.loc[new_df['ค่าใช้จ่าย'] > 90000, 'ค่าใช้จ่าย'] /= 8

# ปัดเศษและแปลงเป็น Int64 (รองรับ NaN)
new_df['ค่าใช้จ่าย'] = new_df['ค่าใช้จ่าย'].round().astype('Int64')

# รวมคอลัมน์มหาวิทยาลัยกับชื่อหลักสูตร
new_df['มหาวิทยาลัย_หลักสูตร'] = new_df['มหาวิทยาลัย'] + " " + new_df['ชื่อหลักสูตร']

# บันทึกไฟล์ใหม่
new_df.to_csv("final_filtered_tcas_cleaned.csv", index=False, encoding='utf-8-sig')

print("บันทึกไฟล์ final_filtered_tcas_cleaned.csv เรียบร้อยแล้ว")
