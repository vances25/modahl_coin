"use client";
import { useRouter } from "next/navigation";
import styles from "./home.module.scss";

export default function Home() {
  const router = useRouter();

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>MODULE COIN EXCHANGE</h1>
      <img className={styles.logo_img} src="/logo.png" alt="logo" />
      <div className={styles.button_container}>
        <button className={styles.button} onClick={() => router.push("/send-coin")}>
          SEND COIN
        </button>
        <button className={styles.button} onClick={() => router.push("/view-balance")}>
          VIEW BALANCE
        </button>
        <button className={styles.button} onClick={() => router.push("/register")}>
          REGISTER
        </button>
      </div>
    </div>
  );
}
