# Copyright (c) Microsoft Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
from typing import Dict

from undetected_playwright.async_api import Browser, BrowserType
from tests.server import Server


async def test_should_expose_video_path(
    browser: Browser, tmpdir: Path, server: Server
) -> None:
    page = await browser.new_page(record_video_dir=tmpdir)
    await page.goto(server.PREFIX + "/grid.html")
    assert page.video
    path = await page.video.path()
    assert str(tmpdir) in str(path)
    await page.context.close()


async def test_short_video_should_throw(
    browser: Browser, tmpdir: Path, server: Server
) -> None:
    page = await browser.new_page(record_video_dir=tmpdir)
    await page.goto(server.PREFIX + "/grid.html")
    assert page.video
    path = await page.video.path()
    assert str(tmpdir) in str(path)
    await page.wait_for_timeout(1000)
    await page.context.close()
    assert os.path.exists(path)


async def test_short_video_should_throw_persistent_context(
    browser_type: BrowserType, tmpdir: Path, launch_arguments: Dict, server: Server
) -> None:
    context = await browser_type.launch_persistent_context(
        str(tmpdir),
        **launch_arguments,
        viewport={"width": 320, "height": 240},
        record_video_dir=str(tmpdir) + "1",
    )
    page = context.pages[0]
    await page.goto(server.PREFIX + "/grid.html")
    await page.wait_for_timeout(1000)
    await context.close()

    assert page.video
    path = await page.video.path()
    assert str(tmpdir) in str(path)


async def test_should_not_error_if_page_not_closed_before_save_as(
    browser: Browser, tmpdir: Path, server: Server
) -> None:
    page = await browser.new_page(record_video_dir=tmpdir)
    await page.goto(server.PREFIX + "/grid.html")
    await page.wait_for_timeout(1000)  # make sure video has some data
    out_path = tmpdir / "some-video.webm"
    assert page.video
    saved = page.video.save_as(out_path)
    await page.close()
    await saved
    await page.context.close()
    assert os.path.exists(out_path)
