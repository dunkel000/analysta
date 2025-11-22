"""
Demo script to try out the analysta package
"""
import analysta as nl
import pandas as pd

print("=" * 60)
print("🖇️  ANALYSTA PACKAGE DEMO")
print("=" * 60)

# Example 1: Basic DataFrame comparison
print("\n📊 Example 1: Basic DataFrame Comparison")
print("-" * 60)
df1 = pd.DataFrame({"id": [1, 2, 3], "price": [100, 200, 300]})
df2 = pd.DataFrame({"id": [2, 3, 4], "price": [200, 250, 400]})

print("DataFrame A:")
print(df1)
print("\nDataFrame B:")
print(df2)

delta = nl.Delta(df1, df2, keys="id")
print(f"\n✅ Rows only in A: {len(delta.unmatched_a)}")
print(delta.unmatched_a)
print(f"\n✅ Rows only in B: {len(delta.unmatched_b)}")
print(delta.unmatched_b)
print(f"\n✅ Changed rows (price column): {len(delta.changed('price'))}")
print(delta.changed("price"))

# Example 2: Tolerant numeric comparison
print("\n\n📊 Example 2: Tolerant Numeric Comparison")
print("-" * 60)
df_a = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.005]})
df_b = pd.DataFrame({"id": [1, 2], "value": [100.0, 200.0]})

print("DataFrame A:")
print(df_a)
print("\nDataFrame B:")
print(df_b)

# With tolerance
delta_tol = nl.Delta(df_a, df_b, keys="id", abs_tol=0.01)
print(f"\n✅ With abs_tol=0.01: {len(delta_tol.changed('value'))} changes")
print(delta_tol.changed("value"))

# Without tolerance
delta_no_tol = nl.Delta(df_a, df_b, keys="id", abs_tol=0.001)
print(f"\n✅ With abs_tol=0.001: {len(delta_no_tol.changed('value'))} changes")
print(delta_no_tol.changed("value"))

# Example 3: Find duplicates
print("\n\n📊 Example 3: Finding Duplicates")
print("-" * 60)
df_dup = pd.DataFrame({"id": [1, 1, 2, 2, 2, 3]})
print("DataFrame with duplicates:")
print(df_dup)

duplicates = nl.duplicates(df_dup, column="id", counts=True)
print("\n✅ Duplicate counts:")
print(duplicates)

# Example 4: Trim whitespace
print("\n\n📊 Example 4: Trimming Whitespace")
print("-" * 60)
df_messy = pd.DataFrame({"id": ["1", "2"], "name": [" Alice ", "  Bob  "]})
print("Before trimming:")
print(df_messy)

df_clean = nl.trim_whitespace(df_messy)
print("\n✅ After trimming:")
print(df_clean)

print("\n" + "=" * 60)
print("✨ Demo complete! Try the web UI with: analysta ui")
print("=" * 60)
