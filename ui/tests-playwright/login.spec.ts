import {expect, test} from "@playwright/test";

declare global {
  interface Window {
    playwrightExtJSRegistered?: boolean;
  }
}

const hostname = "localhost:8080";
const extjsSelector = (selector: string) => `extjs=${selector}`;

test.describe("Login page", () => {
  test.beforeEach(async({page}) => {
    // Register custom selector for ExtJS components
    await page.addInitScript(() => {
      if(typeof window !== "undefined" && !window.playwrightExtJSRegistered){
        window.playwrightExtJSRegistered = true;
        // Custom selector will be registered by page context
      }
    });

    await page.route(/.*\/api\/login\/is_logged.*/, async route => {    
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(false),
      });
    });
    await page.goto(`http://${hostname}/`);
    await page.locator(".x-window").waitFor({state: "visible", timeout: 5000});
  });

  test("should display login dialog with all elements", async({page}) => {
    const loginDialog = page.locator(".x-window");
    const loginButton = page.locator(extjsSelector("[reference=okButton]"));
    
    await expect(loginDialog).toBeVisible();
    await expect(page.getByText("NOC Login")).toBeVisible();
    
    await expect(page.locator(extjsSelector("[reference=loginForm]"))).toBeVisible();
    await expect(page.getByText("User:")).toBeVisible();
    await expect(page.getByText("Password:", {exact: true})).toBeVisible();
    await expect(page.locator('input[name="user"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(loginButton).toBeVisible();
    await expect(page.getByText("Reset")).toBeVisible();
    await expect(loginButton).toHaveClass(/x-btn-disabled/);
  });

  test("should enable Login button when both fields are filled", async({page}) => {
    const loginButton = page.locator(extjsSelector("[reference=okButton]"));
    await expect(loginButton).toHaveClass(/x-btn-disabled/);
    
    await page.locator('input[name="user"]').fill("testuser");
    await expect(loginButton).toHaveClass(/x-btn-disabled/);
    
    await page.locator('input[name="user"]').clear();
    await page.locator('input[name="password"]').fill("password123");
    await expect(loginButton).toHaveClass(/x-btn-disabled/);
    
    await page.locator('input[name="user"]').fill("testuser");
    await page.locator('input[name="password"]').fill("password123");
    
    await expect(loginButton).not.toHaveClass(/x-btn-disabled/);
  });

  test("should show error on invalid login", async({page}) => {
    const loginButton = page.locator(extjsSelector("[reference=okButton]"));

    await page.locator('input[name="user"]').fill("wronguser");
    await page.locator('input[name="password"]').fill("wrongpassword");
    await loginButton.click();
    
    await expect(page.getByText("Failed to log in")).toBeVisible({timeout: 5000});
  });

  test("should navigate to main application on successful login", async({page}) => {
    const loginButton = page.locator(extjsSelector("[reference=okButton]"));

    await page.route(/.*\/api\/login\/login.*/, async route => {    
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({status: true}),
      });
    });

    await page.locator('input[name="user"]').fill("testuser");
    await page.locator('input[name="password"]').fill("password123");
    await loginButton.click();
    
    await expect(page.locator(".x-window")).not.toBeVisible({timeout: 5000});
  });

  test("should reset form fields when clicking Reset button", async({page}) => {
    await page.locator('input[name="user"]').fill("testuser");
    await page.locator('input[name="password"]').fill("password123");
    
    await page.locator("extjs=#resetBtn").click();
    
    await expect(page.locator('input[name="user"]')).toHaveValue("");
    await expect(page.locator('input[name="password"]')).toHaveValue("");
    
    const loginButton = page.locator("extjs=[reference=okButton]");
    await expect(loginButton).toHaveClass(/x-btn-disabled/);
  });
});