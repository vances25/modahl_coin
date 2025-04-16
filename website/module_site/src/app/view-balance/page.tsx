"use client";

import styles from "./style.module.scss";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Send_Coin() {
  const router = useRouter();
  const [wallet, setWallet] = useState("");  // Store input value
  const [result, setResult] = useState("");  // Store API response

  const handleSend = async () => {
    if (!wallet) {
      setResult("Please enter a wallet address.");
      return;
    }

    try {
      const res = await fetch(`https://172-236-101-245.ip.linodeusercontent.com/api/balance/${wallet}`, {
        method: "GET",
      });

      const data = await res.json();
      setResult(data.message || `Balance: ${data.balance} coins`);
    } catch (error) {
      setResult("Error fetching wallet data.");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.navbar}>
        <img 
          onClick={() => router.push("/")} 
          src="/logo.png" 
          alt="logo" 
          className={styles.logo} 
        />
      </div>
      <h1 className={styles.title}>VIEW BALANCES</h1>
      <p className={styles.subtitle}>
        Please note you can use your username or public key for checking balance
      </p>
      <div className={styles.form_group}>
        <label>WALLET:</label>
        <input 
          type="text" 
          placeholder="Enter wallet"
          value={wallet}
          onChange={(e) => setWallet(e.target.value)}
        />
      </div>
      <p>{result}</p>

      <button className={styles.send_button} onClick={handleSend}>
        SEND
      </button>
    </div>
  );
}
