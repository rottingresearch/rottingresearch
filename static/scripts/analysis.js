window.addEventListener('load', () => {
  const links = [...document.getElementsByClassName("analysis-ref")];
  let [success, error403, error404, errorOther] = [0, 0, 0, 0];
  let [numberOfLinks, numberChecked] = [links.length, 0];

  links.forEach((row) => {
    const url = row.getElementsByTagName('input')[0].value;
    const icon = row.getElementsByClassName('analysis-icon')[0];
    const message = row.getElementsByClassName('fetch-response')[0];

    const request = '/check?url=' + encodeURIComponent(url);
    checkHeaders(request).then((response) => {
      message.innerHTML = `<b>${response}</b>`;
      if (Number(response) === 200) {
        icon.innerHTML = '<i class="fa fa-check-circle text-success"></i>';
        success += 1;
        numberChecked += 1;
      } else {
        icon.innerHTML = '<i class="fa fa-exclamation-circle text-failure"></i>';
        if (Number(response) == 403) error403 += 1;
        if (Number(response) == 404) error404 += 1;
        if (Number(response) !== 403 && Number(response) !== 404) {
          errorOther += 1;
          message.innerHTML = `<b>N/A</b>`;
        }
        numberChecked +=1;
      }
    }, (err) => {
      console.error(err);
      icon.innerHTML = '<i class="fa fa-exclamation-circle text-failure"></i>';
      message.innerHTML = "N/A";
      errorOther += 1;
      numberChecked += 1;
    }).finally(() => {
      updateCounts(success, error403, error404, errorOther);
      if (numberOfLinks === numberChecked) {
        const summary = document.getElementsByClassName("linkrot-summary")[0];
        summary.innerHTML = 'Linkrot Summary <i class="fa fa-check"></i>';
        setTimeout(() => summary.innerHTML = 'Linkrot Summary', 2000);
      }
    });
  });
})

function checkHeaders(url) {

  return new Promise((resolve,reject) => {
    const Http = new XMLHttpRequest();
    Http.timeout = 20000;
    Http.open("GET", url, true);

    Http.onreadystatechange = () => {
      if (Http.readyState === 4) {
        resolve(Http.response);
      }
    }

    Http.onerrer = (e) => { reject(e); }

    Http.send();
  })

}

function updateCounts(success, error403, error404, errorOther) {
  
  const currentTime = new Date().getTime();
  const nextHalfSecond = Math.ceil(currentTime/250) * 250;
  const timeOffset = nextHalfSecond - currentTime;

  const elements = [
    {className: "success-200", value: success, singularLabel: "working link"},
    {className: "error-403", value: error403, singularLabel: "403 error"},
    {className: "error-404", value: error404, singularLabel: "404 error"},
    {className: "error-other", value: errorOther, singularLabel: "other error"}];
  
  setTimeout(updateElements, timeOffset)

  function updateElements() {
    elements.forEach(({className, value, singularLabel}) => {
      const summaryBox = document.getElementsByClassName(className)[0];
      const rollup = summaryBox.getElementsByClassName("sum-rollup")[0];
      rollup.innerHTML = value;
      const label = summaryBox.getElementsByClassName("sum-label")[0];
      if (value === 1) {
        label.innerHTML = singularLabel;
      } else {
        label.innerHTML = singularLabel + 's';
      }
    });
  }
}