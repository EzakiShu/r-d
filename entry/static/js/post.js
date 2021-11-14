$('#imgForm').on('submit', function(e) {
    e.preventDefault();
    var formData = new FormData($('#imgForm').get(0));
    $.ajax($(this).attr('action'), {
      type: 'post',
      processData: false,
      contentType: false,
      data: formData,
      success: console.log('send!'); // 送信に成功したとき
    }).done(function(response){
      console.log('succes!');  // レスポンスがあったとき
    }).fail(function() {
       console.log('error!'); // エラーが発生したとき
    });
    return false;
  });
