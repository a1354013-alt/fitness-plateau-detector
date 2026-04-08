function passthrough(input) {
  return typeof input === "string" ? input : String(input ?? "");
}

module.exports = {
  js: passthrough,
  css: passthrough,
  html: passthrough,
  js_beautify: passthrough,
  css_beautify: passthrough,
  html_beautify: passthrough,
};

