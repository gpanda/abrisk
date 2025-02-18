async function fetchDataAndParseJson(url) {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const resp = await response.text()
    return JSON.parse(resp.match(/jsonpgz\((.*)\)/)[1]);
  } catch (error) {
    console.error("Error fetching or parsing data:", error);
    // You might want to return a default value or re-throw the error here
    // depending on how you want to handle errors in your application.
    return null; // Or throw error;
  }
}

async function processData(fundcode) {
  const apiUrl = `http://localhost:8300/etf/${fundcode}`;
  const data = await fetchDataAndParseJson(apiUrl);
  if (data) {
    // Process the data
    console.log("基金名称：", data.name, "基金代码:", data.fundcode,
      "昨日单位净值:", data.dwjz, "估算净值:", data.gsz,
      "估算增长率:", data.gszzl, "估算时间:", data.gztime
    );
  }
}

//processData("513560");

async function getAndDisplayETFData() {
  const fundCode = document.getElementById("fundCodeInput").value;
  if (!fundCode) {
    alert("Please enter a fund code.");
    return;
  }

  console.log(fundCode);
  const apiUrl = `http://localhost:8300/etf/${fundCode}`;
  const data = await fetchDataAndParseJson(apiUrl);

  if (data) {
    const dataDiv = document.getElementById("etfData");
    dataDiv.innerHTML = ""; // Clear previous data

    // Display the data (improved formatting)
    const formattedData = `
          <p><strong>基金名称:</strong> ${data.name}</p>
          <p><strong>基金代码:</strong> ${data.fundcode}</p>
          <p><strong>昨日单位净值:</strong> ${data.dwjz}</p>
          <p><strong>估算净值:</strong> ${data.gsz}</p>
          <p><strong>估算增长率:</strong> ${data.gszzl}%</p>
          <p><strong>估算时间:</strong> ${data.gztime}</p>
        `;
    dataDiv.innerHTML = formattedData;
  } else {
    document.getElementById("etfData").textContent = "Error fetching data. Please check the fund code and try again.";
  }
}

