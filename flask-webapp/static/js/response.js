// Attach an event listener to the form submission button
const submitButton = document.getElementById('submit-button');
submitButton.addEventListener('click', handleFormSubmission);

function add_to_order(item)
{
  document.getElementById('text-prompt').value = `Add ${item} to order.`;
  handleFormSubmission(new MouseEvent("click"));
}
function remove_from_order(item, quantity)
{
  document.getElementById('text-prompt').value = `Remove ${quantity} ${item}.`;
  handleFormSubmission(new MouseEvent("click"));
}
function checkout()
{
  document.getElementById('text-prompt').value = 'Checkout.';
  handleFormSubmission(new MouseEvent("click"));
}
function handleFormSubmission(event) {
  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the value of the text prompt from the form input
  const textPrompt = document.getElementById('text-prompt').value;

  // Create an XHR object to send the text prompt to the server
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/submit-prompt');
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({ textPrompt }));

  // In the XHR's callback function, check the status of the server response
  xhr.onload = () => {
    if (xhr.status === 200) {
      // Extract the response data from the XHR
      const response = xhr.responseText;

      // Display the response on the page
      const responseContainer = document.getElementById('response-container');
      responseContainer.innerHTML += response;
      document.getElementById('text-prompt').value = "";
      document.getElementById('text-prompt').scrollIntoView({ behavior: "auto", block: "end" })
   }
  }
}