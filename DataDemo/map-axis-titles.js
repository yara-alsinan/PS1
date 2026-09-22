const marketMap = document.querySelector("#marketMap");

function addMapAxisTitles() {
  const texts = [...marketMap.querySelectorAll("text")];
  const oldXTitle = texts.find((text) => text.textContent === "one-year return");
  const oldYTitle = texts.find((text) => text.textContent.includes("closer to 52-week high"));
  if (!oldXTitle || marketMap.querySelector(".added-map-axis-titles")) return;
  oldXTitle.remove();
  oldYTitle?.remove();
  const [, , width, height] = marketMap.getAttribute("viewBox").split(" ").map(Number);
  marketMap.insertAdjacentHTML("beforeend", `<g class="added-map-axis-titles"><text class="map-axis chart-title" x="${width / 2}" y="${height - 1}" text-anchor="middle">One-year return (%)</text><text class="map-axis chart-title" transform="translate(13 ${height / 2}) rotate(-90)" text-anchor="middle">Drawdown from 52-week high (%)</text></g>`);
}

const mapObserver = new MutationObserver(() => {
  mapObserver.disconnect();
  addMapAxisTitles();
  mapObserver.observe(marketMap, { childList: true });
});
mapObserver.observe(marketMap, { childList: true });
setTimeout(addMapAxisTitles, 100);
setTimeout(addMapAxisTitles, 500);
