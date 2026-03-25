先看清楚这几个 Section E 表格的结构特点：

- `SectionE_1/2` — 有**两层**：上方的 Info 区（人员信息）+ 下方的 Table 区（明细行，可多行）
- `SectionE_3/4` — 同上，Table 区字段略有不同

每个 Section 的填充模式是一样的，写一个通用方法就够了。

```java
// ══════════════════════════════════════════════════════
// Section E 填充示例（基于 t1141_datasets.xml 结构）
// ══════════════════════════════════════════════════════

// ── Section E-1：Contributor ──────────────────────────
fillSectionEInfo("ContributorInfo_sub", Map.of(
    "SectionE_1_Name",       "Alice Smith",
    "SectionE_1_SIN",        "123456789",
    "SectionE_1_Address",    "100 Main St, New York",
    "SectionE_1_PostalCode", "10001",
    "Section1_CountryCode",  "US"
));

clearTableFirstRow("ContributorTable_sub");   // 删原始空行

// ContributorTable_sub 的行字段是平铺的（无 Row 包裹），每条记录追加一组
addTableRowFlat("ContributorTable_sub", Map.of(
    "SectionE_1_Description", "Cash contribution",
    "RadioButtonGroup",       "1",   // Section1_RadioButton_sf/RadioButtonGroup
    "SectionE_1_Year",        "2024"
));
addTableRowFlat("ContributorTable_sub", Map.of(
    "SectionE_1_Description", "Property contribution",
    "RadioButtonGroup",       "2",
    "SectionE_1_Year",        "2023"
));

// ── Section E-2：Distribution ─────────────────────────
fillSectionEInfo("DistributionInfo_sub", Map.of(
    "SectionE_2_Name",       "Bob Jones",
    "SectionE_2_SIN",        "987654321",
    "SectionE_2_Address",    "200 King St, Toronto",
    "SectionE_2_PostalCode", "M5H3T4",
    "Section2_CountryCode",  "CA"
));

clearTableFirstRow("DistributionTable");

addTableRowFlat("DistributionTable", Map.of(
    "SectionE_2_Description", "Distribution A",
    "SectionE_2_Year",        "2024"
    // TaxCanProperty/RadioButtonGroup 和 NatureOfDistribution/RadioButtonGroup
    // 用嵌套版本处理，见下方
));

// ── Section E-3：Indebted ─────────────────────────────
fillSectionEInfo("IndebtedInfo_sub", Map.of(
    "SectionE_3_Name",        "Carol Lee",
    "SectionE_3_SIN",         "111222333",
    "SectionE_3_Address",     "300 Bay St",
    "SectionE_3_PostalCode",  "M5J2T3",
    "SectionE_3_CountryCode", "CA"
));

clearTableFirstRow("IndebtedTable");

addTableRowFlat("IndebtedTable", Map.of(
    "SectionE_3_Description", "Loan outstanding",
    "SectionE_3_Amount",      "50000"
));

// ── Section E-4：Lender ───────────────────────────────
fillSectionEInfo("LenderInfo_sub", Map.of(
    "SectionE_4_Name",        "David Wang",
    "SectionE_4_SIN",         "444555666",
    "SectionE_4_Address",     "400 Front St",
    "SectionE_4_PostalCode",  "M5V3R6",
    "SectionE_4_CountryCode", "CA"
));

clearTableFirstRow("LenderTable");

addTableRowFlat("LenderTable", Map.of(
    "SectionE_4_Loan",   "Mortgage loan",
    "SectionE_4_Amount", "200000"
));
```

对应的辅助方法：

```java
/**
 * 填充 Section E 的 Info 区（人员信息，非表格，直接设值）。
 * 找到 infoNodeName 容器，把 fields 里的字段逐一设为子节点。
 */
public void fillSectionEInfo(String infoNodeName, Map<String, String> fields) {
    Element docEle = getDoc().getDocumentElement();
    NodeList nl = docEle.getElementsByTagName(infoNodeName);
    if (nl == null || nl.getLength() == 0) {
        System.out.println("[WARN] Info 节点未找到: " + infoNodeName);
        return;
    }
    Element info = (Element) nl.item(0);

    // 先清空已有子节点（原始空节点）
    List<Node> existing = new ArrayList<>();
    NodeList children = info.getChildNodes();
    for (int i = 0; i < children.getLength(); i++)
        if (children.item(i).getNodeType() == Node.ELEMENT_NODE)
            existing.add(children.item(i));
    for (Node n : existing) info.removeChild(n);

    // 按 fields 顺序追加新节点
    for (Map.Entry<String, String> e : fields.entrySet()) {
        if (e.getValue() == null || e.getValue().isBlank()) continue;
        Element child = getDoc().createElement(e.getKey());
        child.setTextContent(e.getValue());
        info.appendChild(child);
    }
}

/**
 * 向平铺结构的表格追加一行（字段直接是表格容器的子节点，无 Row 包裹）。
 *
 * 适用：ContributorTable_sub、DistributionTable、IndebtedTable、LenderTable
 *
 * 对于有嵌套的 RadioButtonGroup（如 Section1_RadioButton_sf/RadioButtonGroup），
 * key 直接写 "RadioButtonGroup"，方法会自动找到容器里第一个同名叶子节点。
 * 如果同一行有多个 RadioButtonGroup 需要区分，用 "父节点名/RadioButtonGroup" 格式。
 */
public void addTableRowFlat(String tableName, Map<String, String> rowData) {
    Element docEle = getDoc().getDocumentElement();
    NodeList nl = docEle.getElementsByTagName(tableName);
    if (nl == null || nl.getLength() == 0) {
        System.out.println("[WARN] 表格未找到: " + tableName);
        return;
    }
    Element table = (Element) nl.item(0);

    for (Map.Entry<String, String> e : rowData.entrySet()) {
        String key   = e.getKey();
        String value = e.getValue();
        if (value == null || value.isBlank()) continue;

        if (key.contains("/")) {
            // "ParentTag/ChildTag" 格式：找 parent 节点再追加 child
            String[] parts  = key.split("/", 2);
            String parentTag = parts[0];
            String childTag  = parts[1];
            NodeList parents = table.getElementsByTagName(parentTag);
            if (parents.getLength() > 0) {
                Element child = getDoc().createElement(childTag);
                child.setTextContent(value);
                parents.item(0).appendChild(child);
            }
        } else {
            // 普通字段：直接追加到 table
            Element child = getDoc().createElement(key);
            child.setTextContent(value);
            table.appendChild(child);
        }
    }
}
```

**结构对照表**，方便你核对参数：

| Section | Info 容器 | Table 容器 | 行字段 |
|---|---|---|---|
| E-1 | `ContributorInfo_sub` | `ContributorTable_sub` | `SectionE_1_Description`, `RadioButtonGroup`, `SectionE_1_Year` |
| E-2 | `DistributionInfo_sub` | `DistributionTable` | `SectionE_2_Description`, `SectionE_2_Year` + 两个嵌套 RadioButtonGroup |
| E-3 | `IndebtedInfo_sub` | `IndebtedTable` | `SectionE_3_Description`, `SectionE_3_Amount` |
| E-4 | `LenderInfo_sub` | `LenderTable` | `SectionE_4_Loan`, `SectionE_4_Amount` |

E-2 的两个嵌套 RadioButtonGroup 如果需要分别设值，用斜杠格式：

```java
addTableRowFlat("DistributionTable", Map.of(
    "SectionE_2_Description",              "Distribution A",
    "TaxCanProperty/RadioButtonGroup",     "1",
    "NatureOfDistribution/RadioButtonGroup","2",
    "SectionE_2_Year",                     "2024"
));
```
