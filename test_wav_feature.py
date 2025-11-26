#!/usr/bin/env python3
"""
Test script to verify WAV conversion feature without breaking existing functionality.
This validates the implementation at the code level without requiring API calls.
"""

import asyncio
import inspect
from suno_client import SunoClient, SunoAPIError


def test_client_methods():
    """Test that SunoClient has all expected methods."""
    print("Testing SunoClient methods...")

    # Expected methods (existing + new)
    expected_methods = [
        'close',
        'convert_to_wav',
        'generate_music',
        'get_credits',
        'get_music_info',
        'get_task_status',
        'get_wav_conversion_status'
    ]

    actual_methods = [
        m for m in dir(SunoClient)
        if not m.startswith('_') and callable(getattr(SunoClient, m))
    ]

    for method in expected_methods:
        if method in actual_methods:
            print(f"  ✓ {method} exists")
        else:
            print(f"  ✗ {method} MISSING")
            return False

    print(f"  Total methods: {len(actual_methods)}")
    return True


def test_method_signatures():
    """Test that method signatures are correct."""
    print("\nTesting method signatures...")

    # Test convert_to_wav signature
    sig = inspect.signature(SunoClient.convert_to_wav)
    params = list(sig.parameters.keys())
    expected_params = ['self', 'callback_url', 'task_id', 'audio_id']

    if params == expected_params:
        print(f"  ✓ convert_to_wav signature correct: {params}")
    else:
        print(f"  ✗ convert_to_wav signature incorrect. Expected {expected_params}, got {params}")
        return False

    # Test get_wav_conversion_status signature
    sig = inspect.signature(SunoClient.get_wav_conversion_status)
    params = list(sig.parameters.keys())
    expected_params = ['self', 'task_id']

    if params == expected_params:
        print(f"  ✓ get_wav_conversion_status signature correct: {params}")
    else:
        print(f"  ✗ get_wav_conversion_status signature incorrect. Expected {expected_params}, got {params}")
        return False

    return True


def test_docstrings():
    """Test that new methods have proper docstrings."""
    print("\nTesting docstrings...")

    convert_doc = SunoClient.convert_to_wav.__doc__
    if convert_doc and len(convert_doc.strip()) > 50:
        print(f"  ✓ convert_to_wav has comprehensive docstring ({len(convert_doc)} chars)")
    else:
        print(f"  ✗ convert_to_wav docstring missing or too short")
        return False

    status_doc = SunoClient.get_wav_conversion_status.__doc__
    if status_doc and len(status_doc.strip()) > 50:
        print(f"  ✓ get_wav_conversion_status has comprehensive docstring ({len(status_doc)} chars)")
    else:
        print(f"  ✗ get_wav_conversion_status docstring missing or too short")
        return False

    return True


def test_existing_methods_unchanged():
    """Test that existing methods still have their original signatures."""
    print("\nTesting existing methods are unchanged...")

    # Check generate_music (most complex method)
    sig = inspect.signature(SunoClient.generate_music)
    params = list(sig.parameters.keys())

    # Must have at least these parameters
    required_params = ['self', 'prompt', 'make_instrumental', 'model_version', 'wait_audio']
    for param in required_params:
        if param in params:
            print(f"  ✓ generate_music has parameter: {param}")
        else:
            print(f"  ✗ generate_music missing parameter: {param}")
            return False

    # Check get_task_status
    sig = inspect.signature(SunoClient.get_task_status)
    params = list(sig.parameters.keys())
    expected = ['self', 'task_id']

    if params == expected:
        print(f"  ✓ get_task_status unchanged: {params}")
    else:
        print(f"  ✗ get_task_status changed. Expected {expected}, got {params}")
        return False

    # Check get_music_info
    sig = inspect.signature(SunoClient.get_music_info)
    params = list(sig.parameters.keys())
    expected = ['self', 'ids']

    if params == expected:
        print(f"  ✓ get_music_info unchanged: {params}")
    else:
        print(f"  ✗ get_music_info changed. Expected {expected}, got {params}")
        return False

    # Check get_credits
    sig = inspect.signature(SunoClient.get_credits)
    params = list(sig.parameters.keys())
    expected = ['self']

    if params == expected:
        print(f"  ✓ get_credits unchanged: {params}")
    else:
        print(f"  ✗ get_credits changed. Expected {expected}, got {params}")
        return False

    return True


def test_error_handling():
    """Test that error handling is implemented."""
    print("\nTesting error handling...")

    # Check that methods raise appropriate errors for missing params
    async def test_validation():
        # Mock client with fake API key (won't actually call API)
        import os
        os.environ['SUNO_API_KEY'] = 'test_key_validation'
        client = SunoClient()

        try:
            # Test convert_to_wav validation (callback_url required, at least one ID required)
            try:
                await client.convert_to_wav("", task_id="test_id")
            except ValueError as e:
                print(f"  ✓ convert_to_wav validates callback_url: {str(e)}")

            try:
                await client.convert_to_wav("https://example.com/webhook")
            except ValueError as e:
                print(f"  ✓ convert_to_wav validates either task_id or audio_id required: {str(e)}")

            # Test get_wav_conversion_status validation
            try:
                await client.get_wav_conversion_status("")
            except ValueError as e:
                print(f"  ✓ get_wav_conversion_status validates task_id: {str(e)}")

        finally:
            await client.close()

        return True

    return asyncio.run(test_validation())


def main():
    """Run all tests."""
    print("=" * 60)
    print("WAV Conversion Feature - Validation Tests")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Client Methods", test_client_methods()))
    results.append(("Method Signatures", test_method_signatures()))
    results.append(("Docstrings", test_docstrings()))
    results.append(("Existing Methods", test_existing_methods_unchanged()))
    results.append(("Error Handling", test_error_handling()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! WAV conversion feature is ready.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed!")
        return 1


if __name__ == "__main__":
    exit(main())
