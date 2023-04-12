function Answer(answx, corrx) {
  this.answ = answx;
  this.corr = corrx;
}
function Question(Q, catx, ans1, ans2, ans3, ans4){
    this.ques = Q;
    this.answ = [];
    answ[0] = new Answer(ans1, true);
    answ[1] = new Answer(ans2, false);
    answ[2] = new Answer(ans3, false);
    answ[3] = new Answer(ans4, false);
    this.cate = catx;
    this.shuffle = function() {
        for (var i = answ.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = answ[i];
            answ[i] = answ[j];
            answ[j] = temp;
        }
    }
    this.check = function(id) {
        return answ[id].corr;
    }
    this.right = function() {
        for(let i = 0; i < answ.length; i++){
            if (answ[i].corr){
                return i;
            }
        }
    }
}