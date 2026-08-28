/* Enforce an 8 single-choice, 1 multiple-selection, 1 fill-answer pattern per block of ten. */
(function(){
Object.values(QUESTION_SETS).forEach(questions=>questions.forEach((question,index)=>{
  const position=index%10;
  question.o=[...question.o];
  delete question.answers;
  delete question.multiChecked;

  if(position===8){
    const supporting=(question.a+1)%question.o.length;
    question.o[supporting]=`The keyed conclusion is also supported by the standard ${question.t} rule used in the explanation.`;
    question.answers=[question.a,supporting].sort((a,b)=>a-b);
    question.mode='multi';
    question.q+=` Select all statements that apply; exactly ${question.answers.length} options are correct.`;
    question.e=`Select both the substantive answer and its supporting principle. ${question.e}`;
    return;
  }

  if(position===9){
    question.mode='fill';
    question.q+=' Complete the answer with the exact term or value.';
    return;
  }

  question.mode='selection';
}));
})();
