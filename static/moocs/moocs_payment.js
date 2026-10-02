/* MOOCS Payment Gateway — Razorpay integration for Sets 3–400.
   This file must load BEFORE moocs.js so the helper functions are available
   when the exam engine assigns its click/change handlers. */

const PREMIUM_SET_START = 3;
let MOOCS_SET_TWO_COMPLETED = JSON.parse(
  document.getElementById('moocs-set-two-completed')?.textContent || 'false'
);
let MOOCS_PREMIUM_ACCESS = JSON.parse(
  document.getElementById('moocs-premium-access')?.textContent || 'false'
);

const getCsrfToken = () => {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.substring(0, name.length + 1) === (name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
};

const isSetPaid = (setNumber) =>
  !setRequiresPayment(setNumber) || MOOCS_PREMIUM_ACCESS;
const setRequiresPayment = (setNumber) => Number(setNumber) >= PREMIUM_SET_START;

const canAccessSet = (setNumber) =>
  !setRequiresPayment(setNumber) ||
  (MOOCS_SET_TWO_COMPLETED && MOOCS_PREMIUM_ACCESS);

let razorpayLoadingPromise = null;
const loadRazorpayScript = () => {
  if (typeof window.Razorpay === 'function') return Promise.resolve();
  if (razorpayLoadingPromise) return razorpayLoadingPromise;

  razorpayLoadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => {
      razorpayLoadingPromise = null;
      reject(new Error('Failed to load Razorpay Checkout SDK'));
    };
    document.head.appendChild(script);
  });

  return razorpayLoadingPromise;
};

const handleSetAccess = async (setNumber) => {
  if (!setRequiresPayment(setNumber)) return true;
  if (isSetPaid(setNumber)) return true;
  if (!MOOCS_SET_TWO_COMPLETED) {
    alert('Complete Set 2 before paying to unlock the remaining sets.');
    return false;
  }

  const email = typeof profileEmail !== 'undefined' ? profileEmail : '';
  if (!email) {
    alert('You must be signed in to access premium sets.');
    return false;
  }

  let createData;
  try {
    const createResponse = await fetch('/MOOCS/payment/create-order/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        set_number: PREMIUM_SET_START,
        email: email,
      }),
    });
    createData = await createResponse.json();
  } catch (e) {
    alert('Unable to connect to the payment server. Please try again.');
    return false;
  }

  if (!createData.success) {
    alert(createData.error || 'Unable to initialize payment. Please try again.');
    return false;
  }

  if (createData.already_paid) {
    MOOCS_PREMIUM_ACCESS = true;
    return true;
  }

  try {
    await loadRazorpayScript();
  } catch (e) {
    alert('Unable to load payment gateway. Please try again.');
    return false;
  }

  return new Promise((resolve) => {
    const options = {
      key: createData.key_id,
      amount: createData.amount,
      currency: createData.currency,
      name: 'MOOCS — TS SET/NET/GATE',
      description: 'One-time access to all remaining MOOCS sets',
      order_id: createData.order_id,
      handler: async (response) => {
        let verifyData;
        try {
          const verifyResponse = await fetch('/MOOCS/payment/verify/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
              set_number: PREMIUM_SET_START,
              email: email,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
            }),
          });
          verifyData = await verifyResponse.json();
        } catch (e) {
          alert('Unable to verify payment. Please try again.');
          resolve(false);
          return;
        }

        if (verifyData.success) {
          MOOCS_PREMIUM_ACCESS = true;
          alert('Payment successful! All remaining MOOCS sets are now unlocked.');
          resolve(true);
        } else {
          alert(verifyData.error || 'Payment verification failed. Please try again.');
          resolve(false);
        }
      },
      theme: { color: '#4f46e5' },
      modal: {
        ondismiss: () => {
          resolve(false);
        },
      },
    };

    const rzp = new Razorpay(options);
    rzp.on('payment.failed', (response) => {
      alert(response.error?.description || 'Payment failed. Please try again.');
      resolve(false);
    });
    rzp.open();
  });
};
