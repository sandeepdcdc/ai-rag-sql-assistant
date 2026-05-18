// import { useState } from "react";
// import axios from "axios";

// function App() {

//   const [question, setQuestion] = useState("");
//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);

//   const askQuestion = async () => {

//     if (!question) return;

//     setLoading(true);

//     try {

//       const response = await axios.post(
//         "http://127.0.0.1:8000/ask",
//         {
//           question: question
//         }
//       );

//       setResult(response.data);

//     } catch (error) {

//       console.error(error);

//       alert("Error fetching result");

//     }

//     setLoading(false);
//   };

//   return (

//     <div
//       style={{
//         minHeight: "100vh",
//         background: "#f5f5f5",
//         padding: "40px"
//       }}
//     >

//       <div
//         style={{
//           maxWidth: "1200px",
//           margin: "auto",
//           background: "white",
//           padding: "30px",
//           borderRadius: "10px"
//         }}
//       >

//         <h1 style={{ marginBottom: "20px" }}>
//           AI RAG LLM
//         </h1>

//         <div
//           style={{
//             display: "flex",
//             gap: "10px"
//           }}
//         >

//           <input
//             type="text"
//             placeholder="Ask your database question..."
//             value={question}
//             onChange={(e) => setQuestion(e.target.value)}
//             style={{
//               flex: 1,
//               padding: "12px",
//               fontSize: "16px"
//             }}
//           />

//           <button
//             onClick={askQuestion}
//             style={{
//               padding: "12px 20px",
//               background: "#007bff",
//               color: "white",
//               border: "none",
//               cursor: "pointer"
//             }}
//           >
//             Ask
//           </button>

//         </div>

//         {loading && (
//           <p style={{ marginTop: "20px" }}>
//             Generating result...
//           </p>
//         )}

//         {result && (

//           <div style={{ marginTop: "40px" }}>

//             <h2>Generated SQL</h2>

//             <pre
//               style={{
//                 background: "#222",
//                 color: "#00ff00",
//                 padding: "20px",
//                 overflow: "auto"
//               }}
//             >
//               {result.sql}
//             </pre>

//             <h2 style={{ marginTop: "30px" }}>
//               Query Result
//             </h2>

//             <div style={{ overflow: "auto" }}>

//               <table
//                 border="1"
//                 cellPadding="10"
//                 style={{
//                   width: "100%",
//                   borderCollapse: "collapse"
//                 }}
//               >

//                 <thead>

//                   <tr>

//                     {result.result &&
//                      result.result.length > 0 &&
//                      Object.keys(result.result[0]).map((key) => (

//                       <th key={key}>
//                         {key}
//                       </th>

//                     ))}

//                   </tr>

//                 </thead>

//                 <tbody>

//                   {result.result &&
//                    result.result.map((row, index) => (

//                     <tr key={index}>

//                       {Object.values(row).map((value, i) => (

//                         <td key={i}>
//                           {value}
//                         </td>

//                       ))}

//                     </tr>

//                   ))}

//                 </tbody>

//               </table>

//             </div>

//           </div>

//         )}

//       </div>

//     </div>
//   );
// }

// export default App;

import { useState } from "react";
import axios from "axios";

function App() {

  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // =========================================
  // FORMAT COLUMN NAME
  // billing_count -> Billing Count
  // branch_name -> Branch Name
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
          maxWidth: "1300px",
          margin: "auto",
          background: "#ffffff",
          padding: "35px",
          borderRadius: "12px",
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
        }}
      >

        {/* ========================================= */}
        {/* HEADER */}
        {/* ========================================= */}

        <h1
          style={{
            marginBottom: "25px",
            color: "#222",
            fontSize: "42px"
          }}
        >
          AI SQL Assistant
        </h1>

        {/* ========================================= */}
        {/* INPUT SECTION */}
        {/* ========================================= */}

        <div
          style={{
            display: "flex",
            gap: "10px",
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
              padding: "14px",
              fontSize: "17px",
              borderRadius: "6px",
              border: "1px solid #ccc",
              outline: "none"
            }}
          />

          <button
            onClick={askQuestion}
            disabled={loading}
            style={{
              padding: "14px 24px",
              background: loading ? "#999" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "16px",
              fontWeight: "bold"
            }}
          >
            {loading ? "Loading..." : "Ask"}
          </button>

        </div>

        {/* ========================================= */}
        {/* LOADING */}
        {/* ========================================= */}

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

        {/* ========================================= */}
        {/* RESULT SECTION */}
        {/* ========================================= */}

        {result && (

          <div style={{ marginTop: "40px" }}>

            {/* ========================================= */}
            {/* GENERATED SQL */}
            {/* ========================================= */}

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

            {/* ========================================= */}
            {/* QUERY RESULT */}
            {/* ========================================= */}

            <h2
              style={{
                marginTop: "35px",
                marginBottom: "15px",
                color: "#222"
              }}
            >
              Query Result
            </h2>

            {/* ========================================= */}
            {/* NO DATA */}
            {/* ========================================= */}

            {(!result.result || result.result.length === 0) ? (

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

                  {/* ========================================= */}
                  {/* TABLE HEADER */}
                  {/* ========================================= */}

                  <thead>

                    <tr
                      style={{
                        background: "#007bff",
                        color: "white"
                      }}
                    >

                      {Object.keys(result.result[0]).map((key) => (

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

                  {/* ========================================= */}
                  {/* TABLE BODY */}
                  {/* ========================================= */}

                  <tbody>

                    {result.result.map((row, index) => (

                      <tr
                        key={index}
                        style={{
                          background:
                            index % 2 === 0 ? "#ffffff" : "#f8f9fa"
                        }}
                      >

                        {Object.values(row).map((value, i) => (

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