function construct_block(url, status){
    var res = $('<li>', {class:'analysis-ref'});
    $('<input>', {type: "hidden", value: url}).appendTo(res);
    var div1 = $('<div>', {class: "check analysis-icon"}).appendTo(res);

    var div2 = $('<div>', {class: "fetch-response"}).appendTo(res);

    if (Number(status)==200) {
        $('<i>', {class: "fa fa-check-circle text-success"}).appendTo(div1);
        $('<b>').text(status).appendTo(div2);
    } else {
        $('<i>', {class: "fa fa-exclamation-circle text-failure"}).appendTo(div1);
        if (Number(status) !==403 && Number(status) !== 404){
            $('<b>').html('N/A').appendTo(div2);
        } else {
            $('<b>').text(status).appendTo(div2);
        }
    }

    var div3 = $('<div>', {class: "link-container"}).appendTo(res);
    var link_a = $('<a>', {class: "pdf-link", target: "_blank", href:url}).text(url).appendTo(div3);

    return res;
}

function fill_document_information(data, container){
    $.each(data, function(key, value){
        var div_title = $('<div>', {class:'meta-title'});
        $("<b>").text(key).appendTo(div_title);
        div_title.appendTo(container);

        $('<div>', {class:'meta-values', style: "white-space: pre-wrap"}).text(value).appendTo(container);
    });
}

function fill_data_gui(data){
    let [success, error403, error404, errorOther] = [0, 0, 0, 0];
    let [numberOfLinks, numberChecked] = [data.value.result_data.length, 0];
    fill_document_information(data.value.metadata, $(".meta-grid"));

    $.each(data.value.result_data, function(key, value){
        if (value.pdfs.length > 0)
        {
            var li = construct_block(value.pdfs[0], value.check[0]);
            $("#pdfs").append(li);
        } else if (value.doi.length > 0)
        {
            var li = construct_block(value.doi[0], value.check[0]);
            $("#doi").append(li);
        } else if (value.arxiv.length > 0)
        {
            var li = construct_block(value.arxiv[0], value.check[0]);
            $("#arxiv").append(li);
        } else if (value.urls.length > 0)
        {
            var li = construct_block(value.urls[0], value.check[0]);
            $("#urls").append(li);
        }


        if (Number(value.check[0]) === 200) {
            success += 1;
            numberChecked += 1;
        } else {
            if (Number(value.check[0]) == 403) error403 += 1;
            if (Number(value.check[0]) == 404) error404 += 1;
            if (Number(value.check[0]) !== 403 && Number(value.check[0]) !== 404) {
              errorOther += 1;
            }
            numberChecked += 1;
        }

     });

    updateCounts(success, error403, error404, errorOther);
    const summary = document.getElementsByClassName("linkrot-summary")[0];
    summary.innerHTML = 'Linkrot Summary <i class="fa fa-check"></i>';
    setTimeout(() => (summary.innerHTML = "Linkrot Summary"), 2000);

    console.log("data");
}
function updateCounts(success, error403, error404, errorOther) {
  const currentTime = new Date().getTime();
  const nextHalfSecond = Math.ceil(currentTime / 250) * 250;
  const timeOffset = nextHalfSecond - currentTime;

  const elements = [
    { className: "success-200", value: success, singularLabel: "working link" },
    { className: "error-403", value: error403, singularLabel: "403 error" },
    { className: "error-404", value: error404, singularLabel: "404 error" },
    {
      className: "error-other",
      value: errorOther,
      singularLabel: "other error",
    },
  ];

  setTimeout(updateElements, timeOffset);

  function updateElements() {
    elements.forEach(({ className, value, singularLabel }) => {
      const summaryBox = document.getElementsByClassName(className)[0];
      const rollup = summaryBox.getElementsByClassName("sum-rollup")[0];
      rollup.innerHTML = value;
      const label = summaryBox.getElementsByClassName("sum-label")[0];
      if (value === 1) {
        label.innerHTML = singularLabel;
      } else {
        label.innerHTML = singularLabel + "s";
      }
    });
  }
}


function get_status(task_id){
    var url = "/result/"+ task_id
    $.get( url)
      .done(function( data ) {
        console.log( data );
        if (data.successful === true){
            fill_data_gui(data);
        } else {
        console.log(" no success");
        setTimeout(get_status, 2000, task_id);
        }
      });
}

$( document ).ready(function() {
    var task_id = $("#taskid").data( "taskid" );
    setTimeout(get_status, 2000, task_id);
});