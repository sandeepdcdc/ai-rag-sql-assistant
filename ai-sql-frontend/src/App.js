import { useState } from "react";
import axios from "axios";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  LineChart,
  Line,
  PieChart,
  Pie,
  Legend,
  LabelList
} from "recharts";

function App() {

  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // =========================================
  // FORMAT COLUMN NAME
  // =========================================

  const formatColumnName = (column) => {

    return column
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase())
      .replace(/\bId\b/g, "ID")
      .trim();

  };

  // =========================================
  // ASK QUESTION
  // =========================================

  const askQuestion = async () => {

    if (!question.trim()) return;

    setLoading(true);

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/ask",
        {
          question: question
        }
      );

      setResult(response.data);

    } catch (error) {

      console.error(error);

      alert("Error fetching result");

    }

    setLoading(false);

  };

  // =========================================
  // AUTO CHART RENDERING
  // =========================================

  const renderChart = () => {

    if (
      !result ||
      !result.result ||
      result.result.length === 0
    ) {
      return null;
    }

    const data = result.result;

    const keys = Object.keys(data[0]);

    if (keys.length < 2) {
      return null;
    }

    const xKey = keys[0];

    const yKey = keys[keys.length - 1];

    // =========================================
    // SMART DISPLAY COLUMN
    // =========================================

    const getDisplayKey = () => {

      const priorityKeys = [

        "month_name",
        "branch_name",
        "patient_name",
        "state_name",
        "full_name",
        "doctor_name"

      ];

      for (const key of priorityKeys) {

        const found = keys.find(
          (k) =>
            k.toLowerCase() === key
        );

        if (found) {

          return found;

        }

      }

      const genericName = keys.find(

        (k) =>

          k.toLowerCase().includes("name")

          &&

          !k.toLowerCase().includes("id")

      );

      if (genericName) {

        return genericName;

      }

      return keys[0];

    };

    const displayKey = getDisplayKey();

    // =========================================
    // AUTO CHART TITLE
    // =========================================

    const generateChartTitle = () => {

      let cleanQuestion = question;

      cleanQuestion = cleanQuestion
        .replace(/\bshow\b/gi, "")
        .replace(/\bgive\b/gi, "")
        .replace(/\blist\b/gi, "")
        .trim();

      return cleanQuestion
        .replace(/\b\w/g, (char) =>
          char.toUpperCase()
        );

    };

    const chartTitle = generateChartTitle();

    // =========================================
    // DYNAMIC LABEL SETTINGS
    // =========================================

    const isLargeDataset = data.length > 6;

    const xAxisAngle = isLargeDataset ? -25 : 0;

    const xAxisHeight = isLargeDataset ? 140 : 100;

    const xAxisFontSize = isLargeDataset ? 11 : 13;

    const chartBottomMargin = isLargeDataset ? 150 : 110;

    // =========================================
    // MONTH TREND -> LINE CHART
    // =========================================

    if (
      xKey.toLowerCase().includes("month")
    ) {

      return (

        <div
          style={{
            width: "100%",
            height: "620px"
          }}
        >

          <h3
            style={{
              textAlign: "center",
              marginBottom: "25px",
              color: "#1f2937",
              fontSize: "34px",
              fontWeight: "700"
            }}
          >
            {chartTitle}
          </h3>

          <ResponsiveContainer
            width="100%"
            height="90%"
          >

            <LineChart
              data={data}
              margin={{
                top: 40,
                right: 30,
                left: 20,
                bottom: chartBottomMargin
              }}
            >

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                dataKey={displayKey}
                interval={0}
                angle={xAxisAngle}
                textAnchor={
                  isLargeDataset
                    ? "end"
                    : "middle"
                }
                height={xAxisHeight}
                tick={{
                  fontSize: xAxisFontSize
                }}
                tickFormatter={(value) => {

                  if (!value) return "";

                  if (value.length > 16) {

                    return value
                      .match(/.{1,16}/g)
                      ?.join("\n");

                  }

                  return value;

                }}
              />

              <YAxis
                tick={{
                  fontSize: 13
                }}
              />

              <Tooltip
                formatter={(value) =>
                  Number(value).toLocaleString()
                }
              />

              <Legend
                verticalAlign="bottom"
                height={40}
                formatter={(value) =>

                  value
                    .replaceAll("_", " ")
                    .replace(/\b\w/g, (c) =>
                      c.toUpperCase()
                    )

                }
              />

              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#1677ff"
                strokeWidth={3}
                dot={{
                  r: 5
                }}
                activeDot={{
                  r: 8
                }}
              >

                <LabelList
                  dataKey={yKey}
                  position="top"
                  formatter={(value) =>
                    Number(value).toLocaleString()
                  }
                />

              </Line>

            </LineChart>

          </ResponsiveContainer>

        </div>

      );

    }

    // =========================================
    // PIE CHART
    // =========================================

    if (
      data.length <= 5 &&
      (
        xKey.toLowerCase().includes("type") ||
        xKey.toLowerCase().includes("category") ||
        xKey.toLowerCase().includes("status")
      )
    ) {

      return (

        <div
          style={{
            width: "100%",
            height: "620px"
          }}
        >

          <h3
            style={{
              textAlign: "center",
              marginBottom: "25px",
              color: "#1f2937",
              fontSize: "34px",
              fontWeight: "700"
            }}
          >
            {chartTitle}
          </h3>

          <ResponsiveContainer
            width="100%"
            height="90%"
          >

            <PieChart>

              <Pie
                data={data}
                dataKey={yKey}
                nameKey={displayKey}
                outerRadius={170}
                fill="#007bff"
                label={({ name, value }) =>
                  `${name}: ${Number(value).toLocaleString()}`
                }
              />

              <Tooltip
                formatter={(value) =>
                  Number(value).toLocaleString()
                }
              />

              <Legend
                formatter={(value) =>

                  value
                    .replaceAll("_", " ")
                    .replace(/\b\w/g, (c) =>
                      c.toUpperCase()
                    )

                }
              />

            </PieChart>

          </ResponsiveContainer>

        </div>

      );

    }

    // =========================================
    // BAR CHART
    // =========================================

    return (

      <div
        style={{
          width: "100%",
          height: "620px"
        }}
      >

        <h3
          style={{
            textAlign: "center",
            marginBottom: "25px",
            color: "#1f2937",
            fontSize: "34px",
            fontWeight: "700"
          }}
        >
          {chartTitle}
        </h3>

        <ResponsiveContainer
          width="100%"
          height="90%"
        >

          <BarChart
            data={data}
            margin={{
              top: 40,
              right: 30,
              left: 20,
              bottom: chartBottomMargin
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey={displayKey}
              interval={0}
              angle={xAxisAngle}
              textAnchor={
                isLargeDataset
                  ? "end"
                  : "middle"
              }
              height={xAxisHeight}
              tick={{
                fontSize: xAxisFontSize
              }}
              tickFormatter={(value) => {

                if (!value) return "";

                if (value.length > 16) {

                  return value
                    .match(/.{1,16}/g)
                    ?.join("\n");

                }

                return value;

              }}
            />

            <YAxis
              tick={{
                fontSize: 13
              }}
            />

            <Tooltip
              formatter={(value) =>
                Number(value).toLocaleString()
              }
            />

            <Legend
              verticalAlign="bottom"
              height={40}
              formatter={(value) =>

                value
                  .replaceAll("_", " ")
                  .replace(/\b\w/g, (c) =>
                    c.toUpperCase()
                  )

              }
            />

            <Bar
              dataKey={yKey}
              fill="#1677ff"
              radius={[8, 8, 0, 0]}
              barSize={55}
            >

              <LabelList
                dataKey={yKey}
                position="top"
                formatter={(value) =>
                  Number(value).toLocaleString()
                }
                style={{
                  fill: "#222",
                  fontSize: 13,
                  fontWeight: "bold"
                }}
              />

            </Bar>

          </BarChart>

        </ResponsiveContainer>

      </div>

    );

  };

  return (

    <div
      style={{
        minHeight: "100vh",
        background: "#f4f6f9",
        padding: "40px",
        fontFamily: "Arial"
      }}
    >

      <div
        style={{
          maxWidth: "1350px",
          margin: "auto",
          background: "#ffffff",
          padding: "35px",
          borderRadius: "14px",
          boxShadow: "0 3px 14px rgba(0,0,0,0.08)"
        }}
      >

        <h1
          style={{
            marginBottom: "25px",
            color: "#222",
            fontSize: "42px"
          }}
        >
          AI SQL Assistant
        </h1>

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "20px"
          }}
        >

          <input
            type="text"
            placeholder="Ask your database question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {

              if (e.key === "Enter") {
                askQuestion();
              }

            }}
            style={{
              flex: 1,
              padding: "15px",
              fontSize: "17px",
              borderRadius: "8px",
              border: "1px solid #ccc",
              outline: "none"
            }}
          />

          <button
            onClick={askQuestion}
            disabled={loading}
            style={{
              padding: "15px 28px",
              background: loading ? "#888" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "16px",
              fontWeight: "bold"
            }}
          >
            {loading ? "Loading..." : "Ask"}
          </button>

        </div>

        {loading && (

          <div
            style={{
              marginTop: "15px",
              color: "#555",
              fontSize: "16px"
            }}
          >
            Generating SQL and fetching results...
          </div>

        )}

        {result && (

          <div style={{ marginTop: "40px" }}>

            <h2
              style={{
                marginBottom: "15px",
                color: "#222"
              }}
            >
              Generated SQL
            </h2>

            <pre
              style={{
                background: "#1e1e1e",
                color: "#00ff66",
                padding: "25px",
                borderRadius: "8px",
                overflowX: "auto",
                fontSize: "15px",
                lineHeight: "1.6"
              }}
            >
              {result.sql}
            </pre>

            {result.result &&
             result.result.length > 0 && (

              <>

                <h2
                  style={{
                    marginTop: "35px",
                    marginBottom: "15px",
                    color: "#222"
                  }}
                >
                  Visualization
                </h2>

                <div
                  style={{
                    background: "#fff",
                    padding: "30px",
                    borderRadius: "10px",
                    boxShadow:
                      "0 2px 10px rgba(0,0,0,0.05)",
                    marginBottom: "25px"
                  }}
                >

                  {renderChart()}

                </div>

              </>

            )}

            <h2
              style={{
                marginBottom: "15px",
                color: "#222"
              }}
            >
              Query Result
            </h2>

            {(!result.result ||
              result.result.length === 0) ? (

              <div
                style={{
                  padding: "20px",
                  background: "#fff3cd",
                  border: "1px solid #ffeeba",
                  borderRadius: "6px",
                  color: "#856404"
                }}
              >
                No data found.
              </div>

            ) : (

              <div
                style={{
                  overflowX: "auto",
                  borderRadius: "8px"
                }}
              >

                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    background: "white"
                  }}
                >

                  <thead>

                    <tr
                      style={{
                        background: "#007bff",
                        color: "white"
                      }}
                    >

                      {Object.keys(
                        result.result[0]
                      ).map((key) => (

                        <th
                          key={key}
                          style={{
                            padding: "14px",
                            border: "1px solid #ddd",
                            textAlign: "left",
                            fontSize: "15px"
                          }}
                        >
                          {formatColumnName(key)}
                        </th>

                      ))}

                    </tr>

                  </thead>

                  <tbody>

                    {result.result.map(
                      (row, index) => (

                      <tr
                        key={index}
                        style={{
                          background:
                            index % 2 === 0
                              ? "#ffffff"
                              : "#f8f9fa"
                        }}
                      >

                        {Object.values(row).map(
                          (value, i) => (

                          <td
                            key={i}
                            style={{
                              padding: "12px",
                              border: "1px solid #ddd",
                              fontSize: "15px"
                            }}
                          >
                            {value}
                          </td>

                        ))}

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        )}

      </div>

    </div>

  );

}

export default App;