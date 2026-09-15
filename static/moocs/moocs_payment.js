/* MOOCS Payment Gateway — Razorpay integration for Set 3 access.
   This file must load BEFORE moocs.js so the helper functions are available
   when the exam engine assigns its click/change handlers. */

const MOCS_SET_3_FEE = 499.00;
const SETS_REQUIRING_PAYMENT = [3];
const PAID_SETS_KEY_PREFIX = 'moocs-paid-sets:';

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

const getPaidSetsKey = () =>
  typeof profileEmail !== 'undefined' && profileEmail
    ? `${PAID_SETS_KEY_PREFIX}${profileEmail}`
    : null;

const readPaidSets = () => {
  const key = getPaidSetsKey();
  if (!key) return [];
  try {
    return JSON.parse(localStorage.getItem(key) || '[]');
  } catch (e) {
    return [];
  }
};

const writePaidSets = (sets) => {
  const key = getPaidSetsKey();
  if (!key) return;
  try {
    localStorage.setItem(key, JSON.stringify(sets));
  } catch (e) {
    /* Silent — the exam remains usable when storage is unavailable. */
  }
};

const isSetPaid = (setNumber) => readPaidSets().includes(setNumber);

const markSetPaid = (setNumber) => {
  const sets = readPaidSets();
  if (!sets.includes(setNumber)) writePaidSets([...sets, setNumber]);
};

const setRequiresPayment = (setNumber) => SETS_REQUIRING_PAYMENT.includes(setNumber);

const canAccessSet = (setNumber) => !setRequiresPayment(setNumber) || isSetPaid(setNumber);

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
        set_number: setNumber,
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
    markSetPaid(setNumber);
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
      description: `Access to Set ${setNumber} mock examination`,
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
              set_number: setNumber,
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
          markSetPaid(setNumber);
          alert(`Payment successful! Set ${setNumber} is now unlocked.`);
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
    rzp.open();
  });
};
