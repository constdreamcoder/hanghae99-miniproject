'use strict'

const storeBtnContainer = document.querySelector('.store_categories');
const datailListContainer = document.querySelector('.detail-list');
const detailItems = document.querySelectorAll('.detail-item');

// 지역 버튼 클릭시 버튼의 data 값을 확인한다.
storeBtnContainer.addEventListener('click', (e) => {
    const filter = e.target.dataset.filter;
    // console.log(filter)
    // data 값이 null 이면 아무것도 하지 않고 끝난다.
    if (filter == null) {
        return;
    }

    // 가게의 item을 반복문 시켜 지역 버튼과 data 값이 같은지 확인한다.
    detailItems.forEach((item) => {
        //
        // console.log(item.dataset.type)
        if (filter === "*" || filter === item.dataset.type) {
            // 버튼의 data값이 item의 값이 같거나 모두 일치할때 해당 item에 invisible의 클래스를 해제하여 display:black으로 된다.
            item.classList.remove('invisible');
        } else {
            // 그것이 아닌때는 invisible이 붙어 display:none 상태가 된다.
            item.classList.add('invisible')
        }
    })
})

// arrow up btn 찾아주기
const arrowUp = document.querySelector('.arrow-up')

// btn 누르면 scrollTo 함수를 실행시켜 header로 이동
arrowUp.addEventListener('click', () => {
  scrollTo('#header');
})

// selector를 한곳으로 이동하게 만들어주는 function.
function scrollTo(selector) {
  const scrollTo = document.querySelector(selector)
  scrollTo.scrollIntoView({
    behavior: "smooth"
  });
}