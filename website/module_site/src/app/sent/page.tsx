"use client";

import styles from "./style.module.scss";
import { useRouter } from "next/navigation";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function Send_Coin_Content() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const amount = searchParams.get("amount");
  const wallet = searchParams.get("wallet");

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
      <h1 className={styles.title}>SENT SUCCESSFULLY</h1><br/>
      <h3>{amount || ""} coins sent to</h3><br/>
      <h4>{wallet || ""}</h4><br/>
      <button className={styles.send_button} onClick={() => router.push("/")}>
        BACK HOME
      </button>
    </div>
  );
}

export default function Send_Coin() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Send_Coin_Content />
    </Suspense>
  );
}
